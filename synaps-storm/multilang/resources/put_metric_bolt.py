# -*- coding:utf-8 -*-
# Copyright 2012 Samsung SDS

import os
import sys
import operator
from uuid import uuid4, UUID

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
from synaps.rpc import PUT_METRIC_DATA_MSG_ID, PUT_METRIC_ALARM_MSG_ID, \
    DELETE_ALARMS_MSG_ID

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
    
    CMP_MAP = {
        'GreaterThanOrEqualToThreshold':  operator.ge,
        'GreaterThanThreshold': operator.gt,
        'LessThanThreshold': operator.lt,
        'LessThanOrEqualToThreshold': operator.le,
    }

    CMP_STR_MAP = {
        'GreaterThanOrEqualToThreshold': "greater than or equal to",
        'GreaterThanThreshold': "greater than",
        'LessThanThreshold': "less than",
        'LessThanOrEqualToThreshold': "less than or equal to",
    }    
    
    
    def __init__(self, metric_key, cass):
        self.metric_key = metric_key
        self.cass = cass
        self.df = self.load_statistics()
        self.alarms = self.load_alarms()
        self.lastchecked = None

    def _reindex(self):
        self.df = self.df.reindex(index=self._get_range())

    def _get_range(self):
        now_idx = datetime.utcnow().replace(second=0, microsecond=0)
        start = now_idx - timedelta(seconds=self.STATISTICS_TTL)
        end = now_idx + timedelta(seconds=60 * 60) # 1 HOUR
        daterange = DateRange(start, end, offset=datetools.Minute())
        return daterange

    def delete_metric_alarm(self, alarmkey):
        """
        메모리 및 DB에서 알람을 삭제한다.
        
        alarmkey:
            alarmkey should be UUID
        """
        alarm = self.alarms.pop(alarmkey)
        self.cass.delete_metric_alarm(alarmkey)
        self.alarm_history_delete(alarmkey, alarm)
        storm.log("delete alarm %s for metric %s" % (str(alarmkey),
                                                     self.metric_key))
                                                        
    def load_statistics(self):
        stat = self.cass.load_statistics(self.metric_key)
        if stat:
            df = DataFrame(stat, index=self._get_range())
        else:
            df = DataFrame(columns=self.COLUMNS, index=self._get_range())
        return df
    
    def load_alarms(self):
        alarms = dict(self.cass.load_alarms(self.metric_key))
        storm.log("load_alarms %s for metric %s" % (str(alarms),
                                                    self.metric_key))
        return alarms

    def get_metric_statistics(self, window, statistics, start=None, end=None,
                              unit=None):
        df = self.df.ix[start:end] if start and end else self.df
        
        ret_dict = {}
        for statistic in statistics:
            func = self.ROLLING_FUNC_MAP[statistic]
            ret_dict[statistic] = func(df[statistic], window)
        
        return DataFrame(ret_dict)
    
    def put_alarm(self, project_id, metricalarm):
        alarm_name = metricalarm.get('alarm_name')
        alarm_key = self.cass.get_metric_alarm_key(project_id, alarm_name)
        if alarm_key:
            self.alarms[alarm_key] = self.cass.get_metric_alarm(alarm_key)
        else:
            storm.log("no alarm key [%s]" % alarm_key)

    def put_metric_data(self, timestamp, value, unit=None):
        time_idx = timestamp.replace(second=0, microsecond=0)
        if time_idx not in self.df.index:
            self._reindex()
        
        value = utils.to_default_unit(value, unit)
        
        try:
            stat = self.df.ix[time_idx]
        except KeyError:
            storm.log("index %s in not in the time range." % time_idx)
            return
        
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
        storm.log("metric data inserted %s" % (self.metric_key))
        
        # check alarms
        self.check_alarms()
    
    def check_alarms(self):
        for k, v in self.alarms.iteritems():
            self._check_alarm(k, v)
        self.lastchecked = utils.utcnow()
            
    def _check_alarm(self, alarmkey, alarm):
        period = int(alarm['period'] / 60)
        evaluation_period = alarm['evaluation_period']
        statistic = alarm['statistic']
        threshold = alarm['threshold']
        cmp_op = self.CMP_MAP[alarm['comparison_operator']]
        unit = alarm['unit']
        state_value = alarm['state_value']
        
        now = utils.utcnow()
        end_idx = now.replace(second=0, microsecond=0)
        start_idx = end_idx - evaluation_period * datetools.Minute()
        start_ana_idx = start_idx - datetools.Minute() * period
        
        func = self.ROLLING_FUNC_MAP[statistic]
        data = func(self.df[statistic].ix[start_ana_idx:end_idx], period,
                    min_periods=0).ix[start_idx:end_idx]
        if unit:
            data = data / utils.UNIT_CONV_MAP[unit]
            threshold = threshold / utils.UNIT_CONV_MAP[unit] 
        
        if statistic == 'SampleCount':
            data = data.fillna(0)
        else:
            data = data.dropna()

        reason_data = {
            "period":alarm['period'],
            "queryDate":utils.strtime(now),
            "recentDatapoints": list(data),
            "startDate": utils.strtime(start_idx),
            "statistic":statistic,
            "threshold": threshold,
            "version":"1.0",
        }
        old_state = {'stateReason':alarm.get('reason', ""),
                     'stateValue':alarm.get('state_value',
                                            "INSUFFICIENT_DATA"),
                     'stateReasonData':
                        json.loads(alarm.get('reason_data', "{}"))}
        json_reason_data = json.dumps(reason_data)

        storm.log("data \n %s" % data)
        if len(data) < evaluation_period:
            if state_value != 'INSUFFICIENT_DATA':
                template = _("Insufficient Data: %d datapoints were unknown.")
                reason = template % (evaluation_period - len(data))
                new_state = {'stateReason':reason,
                             'stateReasonData':reason_data,
                             'stateValue':'INSUFFICIENT_DATA'}
                self.update_alarm_state(alarmkey, 'INSUFFICIENT_DATA', reason,
                                        json_reason_data, now)
                self.cass.update_alarm_state(alarmkey, 'INSUFFICIENT_DATA',
                                             reason, json_reason_data, now)
                self.alarm_history_state_update(alarmkey, alarm,
                                                new_state, old_state)
                storm.log("INSUFFICIENT_DATA alarm")
        else:
            crossed = reduce(operator.and_, cmp_op(data, threshold))
            com_op = alarm['comparison_operator']
            
            if crossed:
                template = _("Threshold Crossed: %d datapoints were %s " + 
                             "the threshold(%f). " + 
                             "The most recent datapoints: %s.")
                reason = template % (len(data),
                                     self.CMP_STR_MAP[com_op],
                                     threshold, str(list(data)))
                if state_value != 'ALARM':
                    new_state = {'stateReason':reason,
                                 'stateReasonData':reason_data,
                                 'stateValue':'ALARM'}
                    
                    self.update_alarm_state(alarmkey, 'ALARM', reason,
                                            json_reason_data, now)
                    self.cass.update_alarm_state(alarmkey, 'ALARM', reason,
                                                 json_reason_data, now)
                    self.alarm_history_state_update(alarmkey, alarm,
                                                    new_state, old_state)                    
                    storm.log("ALARM alarm")
            else:
                template = _("Threshold Crossed: %d datapoints were not %s " + 
                             "the threshold(%f). " + 
                             "The most recent datapoints: %s.")
                reason = template % (len(data),
                                     self.CMP_STR_MAP[com_op],
                                     threshold, str(list(data)))
                if state_value != 'OK':
                    new_state = {'stateReason':reason,
                                 'stateReasonData':reason_data,
                                 'stateValue':'OK'}                    
                    self.update_alarm_state(alarmkey, 'OK', reason,
                                            json_reason_data, now)
                    self.cass.update_alarm_state(alarmkey, 'OK', reason,
                                                 json_reason_data, now)
                    self.alarm_history_state_update(alarmkey, alarm,
                                                    new_state, old_state)                            
                    storm.log("OK alarm")
            
            storm.log("check %s %f" % (alarm['comparison_operator'],
                                       threshold))
            storm.log("result \n %s" % crossed)
    
    def alarm_history_delete(self, alarm_key, alarm):
        item_type = 'ConfigurationUpdate'
        summary = "Alarm %s deleted" % alarm['alarm_name']
        
        history_key = uuid.uuid4()
        history_column = {
            'project_id': alarm['project_id'],
            'alarm_key': alarm_key,
            'alarm_name': alarm['alarm_name'],
            'history_data': json.dumps({'type': 'Delete', 'version': '1.0'}),
            'history_item_type': item_type,
            'history_summary': summary,
            'timestamp': utils.utcnow()
        }
        
        self.cass.insert_alarm_history(history_key, history_column)
        
    
    def alarm_history_state_update(self, alarmkey, alarm, new_state,
                                          old_state):
        item_type = 'StateUpdate'
        project_id = alarm['project_id']
        summary_tpl = "Alarm updated from %s to %s" 
        summary = summary_tpl % (old_state.get('stateValue',
                                               'INSUFFICIENT_DATA'),
                                 new_state.get('stateValue',
                                               'INSUFFICIENT_DATA'))
        timestamp = utils.utcnow()
        data = {'newState':new_state, 'oldState':old_state, 'version':'1.0'}

        history_key = uuid.uuid4()
        column = {'project_id':project_id, 'alarm_key':alarmkey,
                  'alarm_name':alarm['alarm_name'],
                  'history_data':json.dumps(data),
                  'history_item_type':item_type, 'history_summary':summary,
                  'timestamp':timestamp}
        
        self.cass.insert_alarm_history(history_key, column)
        storm.log("alarm history \n %s" % summary)
                
    def update_alarm_state(self, alarmkey, state_value, reason, reason_data,
                           timestamp):
        alarm = self.alarms[alarmkey]
        alarm['state_value'] = state_value
        alarm['reason'] = reason
        alarm['reason_data'] = reason_data
        alarm['state_updated_timestamp'] = timestamp        
            

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
    
    def process_put_metric_alarm_msg(self, metric_key, message):
        if metric_key not in self.metrics:
            self.metrics[metric_key] = MetricMonitor(metric_key, self.cass)
        project_id = message['project_id']
        metricalarm = message['metricalarm']
        self.metrics[metric_key].put_alarm(project_id, metricalarm)

    def process_delete_metric_alarms_msg(self, metric_key, message):
        alarmkey = UUID(message['alarmkey'])
        storm.log("debug: %s" % self.metrics.keys())
        if metric_key not in self.metrics:
            self.metrics[metric_key] = MetricMonitor(metric_key, self.cass)
        self.metrics[metric_key].delete_metric_alarm(alarmkey)
        
    def process(self, tup):
        metric_key = UUID(tup.values[0])
        message = json.loads(tup.values[1])
        message_id = message.get('message_id')
        
        try:
            if message_id == PUT_METRIC_DATA_MSG_ID:
                storm.log("process put_metric_data_msg (%s)" % message)
                self.process_put_metric_data_msg(metric_key, message)
            elif message_id == PUT_METRIC_ALARM_MSG_ID:
                storm.log("process put_metric_alarm_msg (%s)" % message)
                self.process_put_metric_alarm_msg(metric_key, message)
            elif message_id == DELETE_ALARMS_MSG_ID:
                storm.log("process put_metric_alarm_msg (%s)" % message)
                self.process_delete_metric_alarms_msg(metric_key, message)
            else:
                storm.log("unknown message")
        except Exception as e:
            storm.log(traceback.format_exc(e))
            storm.fail(tup)

if __name__ == "__main__":
    flags.FLAGS(sys.argv)
    utils.default_flagfile()
    logging.setup()
    PutMetricBolt().run()
