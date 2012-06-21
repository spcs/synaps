# -*- coding:utf-8 -*-
# Copyright 2012 Samsung SDS
# All Rights Reserved

import time

from datetime import datetime, timedelta
from pandas import TimeSeries, DataFrame, DateRange, datetools
from pandas import (rolling_sum, rolling_max, rolling_min, rolling_mean)
from numpy import isnan

from pprint import pformat

from synaps import flags
from synaps import log as logging
from synaps.db import Cassandra
from synaps import rpc
from synaps import utils
from synaps.exception import RpcInvokeException, Invalid

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS    


class API(object):
    ROLLING_FUNC_MAP = {
        'Average': rolling_mean,
        'Minimum': rolling_min,
        'Maximum': rolling_max,
        'SampleCount': rolling_sum,
        'Sum': rolling_sum,
    }
    
    def __init__(self):
        self.cass = Cassandra()
        self.rpc = rpc.RemoteProcedureCall()
    
    def put_metric_alarm(self, project_id, metricalarm):
        """
        알람을 DB에 넣고 값이 빈 dictionary 를 반환한다.
        
        메트릭 유무 확인
        
        알람 히스토리 발생.
        """
        # 메트릭 유무 확인
        metric_key = self.cass.get_metric_key(
            project_id=project_id,
            namespace=metricalarm.namespace,
            metric_name=metricalarm.metric_name,
            dimensions=metricalarm.dimensions
        )
        
        if not metric_key:
            raise Invalid(_("invalid metric information"))

        message = {'project_id': project_id, 'metric_key': str(metric_key),
                   'metricalarm': metricalarm.to_columns()}
        self.rpc.send_msg(rpc.PUT_METRIC_ALARM_MSG_ID, message)
        LOG.info("PUT_METRIC_ALARM_MSG sent")

        return {}
    
    def put_metric_data(self, project_id, namespace, metric_data):
        """
        metric data 를 입력받아 MQ 에 넣고 값이 빈 dictionary 를 반환한다.        
        """
        for metric in utils.extract_member_list(metric_data):
            dimensions = utils.extract_member_dict(metric.get('dimensions'))
            metric_name = metric.get('metric_name')
            unit = metric.get('unit', 'None')
            value = metric.get('value')
            req_timestamp = metric.get('timestamp')
            timestamp = req_timestamp if req_timestamp \
                        else utils.strtime(utils.utcnow()) 
            
            # pack message
            message = {'project_id': project_id, 'namespace':namespace,
                       'metric_name': metric_name, 'dimensions': dimensions,
                       'value':value, 'unit':unit, 'timestamp':timestamp}
            
            self.rpc.send_msg(rpc.PUT_METRIC_DATA_MSG_ID, message)
            LOG.info("PUT_METRIC_DATA_MSG sent")
            
        return {}

    def list_metrics(self, project_id, next_token=None, dimensions=None,
                     metric_name=None, namespace=None):
        """
        입력받은 조건과 일치하는 메트릭의 리스트를 반환한다.
        """
        metrics = self.cass.list_metrics(project_id, namespace, metric_name,
                                         dimensions, next_token)
        return metrics

    def get_metric_statistics(self, project_id, end_time, metric_name,
                              namespace, period, start_time, statistics,
                              unit=None, dimensions=None):
        """
        입력받은 조건에 일치하는 메트릭의 통계자료 리스트를 반환한다.
        """
        def to_datapoint(df, idx):
            datapoint = df.ix[idx].dropna()
            if len(datapoint):
                return idx, datapoint
        
        end_idx = end_time.replace(second=0, microsecond=0)
        start_idx = start_time.replace(second=0, microsecond=0)
        daterange = DateRange(start_idx, end_idx, offset=datetools.Minute())

        # load default unit for metric from database
        if unit == "None" or not unit:
            metric_key = self.cass.get_metric_key(
                project_id=project_id, namespace=namespace,
                metric_name=metric_name, dimensions=dimensions
            )
            
            if metric_key:
                unit = self.cass.get_metric_unit(metric_key)
            else:
                unit = "None"
        
        # load statistics data from database
        stats = self.cass.get_metric_statistics(
            project_id=project_id, namespace=namespace,
            metric_name=metric_name, start_time=start_time, end_time=end_time,
            period=period, statistics=statistics, dimensions=dimensions
        )
        
        period = period / 60 # convert sec to min
        stat = DataFrame(index=daterange)
        
        for statistic, series in zip(statistics, stats):
            func = self.ROLLING_FUNC_MAP[statistic]
            ts = TimeSeries(series, index=daterange)
            if statistic == 'SampleCount':
                ts = ts.fillna(0)
            stat[statistic] = func(ts, period, min_periods=0)

        ret = filter(None, (to_datapoint(stat, i) for i in stat.index))
        return ret
