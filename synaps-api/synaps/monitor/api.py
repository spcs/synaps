# Copyright 2012 Samsung SDS
# All Rights Reserved

import time

from synaps import flags
from synaps import log as logging
from synaps.db import Cassandra
from synaps import rpc
from synaps import utils
from synaps.exception import RpcInvokeException

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS    

class Metric(object):
    pass

class Alarm(object):
    pass

class API(object):
    def __init__(self):
        self.cass = Cassandra()
        self.rpc = rpc.RemoteProcedureCall()
    
    def put_metric_alarm(self, metric, alarm):
        """
        메시지를 MQ 에 넣고 값이 빈 dictionary 를 반환한다.
        """
        def pack(metric, alarm):
            return {}
        
        message = pack(metric, alarm)
        self.rpc.send_msg(rpc.PUT_METRIC_ALARM_MSG_ID, message)
       
        return {}
    
    def put_metric_data(self, project_id, namespace, metric_data):
        """
        metric data 를 입력받아 MQ 에 넣고 값이 빈 dictionary 를 반환한다.        
        """
        for metric in utils.extract_member_list(metric_data):
            dimensions = utils.extract_member_dict(metric.get('dimensions'))
            metric_name = metric.get('metric_name')
            unit = metric.get('unit', None)
            value = metric.get('value')
            req_timestamp = metric.get('timestamp')
            timestamp = req_timestamp if req_timestamp \
                        else utils.parse_strtime(utils.utcnow()) 
            
            # pack message
            message = {'project_id': project_id, 'namespace':namespace,
                       'metric_name': metric_name, 'dimensions': dimensions,
                       'value':value, 'unit':unit, 'timestamp':timestamp}
            
            self.rpc.send_msg(rpc.PUT_METRIC_DATA_MSG_ID, message)
            
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
                              unit="None", dimensions=None):
        """
        입력받은 조건에 일치하는 메트릭의 통계자료 리스트를 반환한다.
        """
        stats = self.cass.get_metric_statistics(project_id=project_id,
                                                namespace=namespace,
                                                metric_name=metric_name,
                                                start_time=start_time,
                                                end_time=end_time,
                                                period=period,
                                                statistics=statistics,
                                                unit=unit,
                                                dimensions=dimensions)
        return stats
        
