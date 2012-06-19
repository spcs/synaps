# -*- coding:utf-8 -*-
# Copyright 2012 Samsung SDS

import os
import sys

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "synaps", "__init__.py")):
    sys.path.insert(0, possible_topdir)

import traceback
import storm
import json
import uuid

from datetime import datetime, timedelta
from pandas import TimeSeries, DataFrame, DateRange, datetools
from pandas import rolling_sum, rolling_max, rolling_min, rolling_mean
from numpy import isnan

from synaps import flags
from synaps import log as logging
from synaps import utils
from synaps.db import Cassandra
from synaps.rpc import PUT_METRIC_DATA_MSG_ID, PUT_METRIC_ALARM_MSG_ID


class MetricMonitor(object):
    COLUMNS = Cassandra.STATISTICS
    STATISTICS_TTL = Cassandra.STATISTICS_TTL
    ROLLING_FUNC_MAP = {
        'Average': rolling_mean,
        'Minimum': rolling_min,
        'Maximum': rolling_max,
        'SampleCount': rolling_sum,
        'Sum': rolling_sum,
    }

    def __init__(self, metric_key, cass):
        self.metric_key = metric_key
        self.cass = cass
        self.load_statistics()
        self.load_alarms()        

    def _reindex(self):
        self.df = self.df.reindex(index=self._get_range())

    def _get_range(self):
        now_idx = datetime.utcnow().replace(second=0, microsecond=0)
        start = now_idx - timedelta(seconds=self.STATISTICS_TTL)
        end = now_idx + timedelta(seconds=60 * 60) # 1 HOUR
        daterange = DateRange(start, end, offset=datetools.Minute())
        return daterange
    
    def load_statistics(self):
        stat = self.cass.load_statistics(self.metric_key)
        if stat:
            self.df = DataFrame(stat, index=self._get_range())
        else:
            self.df = DataFrame(columns=self.COLUMNS, index=self._get_range())
    
    def load_alarms(self):
        pass

    def get_metric_statistics(self, window, statistics, start=None,
                              end=None, unit=None):
        df = self.df.ix[start:end] if start and end else self.df
        
        ret_dict = {}
        for statistic in statistics:
            func = self.ROLLING_FUNC_MAP[statistic]
            ret_dict[statistic] = func(df[statistic], window)
        
        return DataFrame(ret_dict)

    def put_metric_data(self, timestamp, value, unit=None):
        time_idx = timestamp.replace(second=0, microsecond=0)
        if time_idx not in self.df.index:
            self._reindex()
        
        value = utils.to_default_unit(value, unit)
            
        stat = self.df.ix[time_idx]
        
        stat['SampleCount'] = 1.0 if isnan(stat['SampleCount']) \
                              else stat['SampleCount'] + 1.0
        stat['Sum'] = value if isnan(stat['Sum'])  \
                      else stat['Sum'] + value
        stat['Average'] = stat['Sum'] / stat['SampleCount']
        stat['Minimum'] = value \
                          if isnan(stat['Minimum']) or stat['Minimum'] > value \
                          else stat['Minimum']
        stat['Maximum'] = value \
                          if isnan(stat['Maximum']) or stat['Maximum'] < value \
                          else stat['Maximum']

        # insert into DB
        stat_dict = {
            'SampleCount':{time_idx: stat['SampleCount']},
            'Sum':{time_idx: stat['Sum']},
            'Average':{time_idx: stat['Average']},
            'Minimum':{time_idx: stat['Minimum']},
            'Maximum':{time_idx: stat['Maximum']}
        }
        
        self.cass.insert_stat(self.metric_key, stat_dict)
        

class PutMetricBolt(storm.BasicBolt):
    def initialize(self, stormconf, context):
        self.cass = Cassandra()
        self.metrics = {}
    
    def process_put_metric_data_msg(self, metric_key, message):
        """
        데이터베이스에 MetricArchive 컬럼패밀리에 입력된 값 추가. 메모리
        (self.metrics)에도 입력된 값 추가.
        
        메모리 상의 메트릭을 기반으로 데이터베이스에 StatArchive 컬럼패밀리 
        업데이트.
        """
        # 메시지 값이 없는 경우 종료    
        if message['value'] is None:
            return
        
        # 메트릭 가져오기
        if metric_key not in self.metrics:
            self.metrics[metric_key] = MetricMonitor(metric_key, self.cass)

        timestamp = utils.parse_strtime(message['timestamp'])

        self.metrics[metric_key].put_metric_data(
            timestamp=timestamp, value=message['value'], unit=message['unit']
        )
        
        storm.log("metric data inserted %s" % (metric_key))
    
    def process_put_metric_alarm_msg(self, metric_key, message):
        project_id = message['project_id']
        metricalarm = message['metricalarm']
        self.cass.put_metric_alarm(project_id, metric_key, metricalarm)
        storm.log("metric alarm inserted %s" % (metric_key))
        
    def process(self, tup):
        metric_key = uuid.UUID(tup.values[0])
        message = json.loads(tup.values[1])
        message_id = message.get('message_id')
        
        try:
            if message_id == PUT_METRIC_DATA_MSG_ID:
                storm.log("process put_metric_data_msg (%s)" % message)
                self.process_put_metric_data_msg(metric_key, message)
            elif message_id == PUT_METRIC_ALARM_MSG_ID:
                storm.log("process put_metric_alarm_msg (%s)" % message)
                self.process_put_metric_alarm_msg(metric_key, message)
            else:
                storm.log("unknown message")
        except Exception as e:
            storm.log(traceback.format_exc(e))
            

if __name__ == "__main__":
    flags.FLAGS(sys.argv)
    utils.default_flagfile()
    logging.setup()
    PutMetricBolt().run()
