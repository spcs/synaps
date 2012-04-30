# Copyright 2012 Samsung SDS
# All Rights Reserved

import time

from synaps import flags
from synaps import log as logging
from synaps.db import Cassandra
from synaps.rpc import RemoteProcedureCall
from synaps import utils
from synaps.exception import RpcInvokeException

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS    

class API(object):
    def __init__(self):
        self.cass = Cassandra()
        self.rpc = RemoteProcedureCall()
    
    def put_metric_data(self, project_id, namespace, metric_data):
        for metric in utils.extract_member_list(metric_data):
            dimensions = utils.extract_member_dict(metric.get('dimensions'))
            metric_name = metric.get('metric_name')
            unit = metric.get('unit', None)
            value = metric.get('value')
            req_timestamp = metric.get('timestamp')
            timestamp = utils.parse_strtime(req_timestamp) \
                        if req_timestamp else utils.utcnow() 
            
            try:
                self.rpc.put_metric_data(project_id, namespace, metric_name,
                                         dimensions, value, unit, timestamp)
            except RpcInvokeException:
                LOG.warn(_("RPC has failed. Access to the DB directly."))
                self.cass.put_metric_data(project_id, namespace, metric_name,
                                          dimensions, value, unit, timestamp)
        return {}

    def list_metrics(self, project_id, next_token=None, dimensions=None,
                     metric_name=None, namespace=None):
        metrics = self.cass.list_metrics(project_id, namespace, metric_name,
                                         dimensions, next_token)
        return metrics

    def get_metric_statistics(self, project_id, end_time, metric_name,
                              namespace, period, start_time, statistics,
                              unit="None", dimensions=None):
        
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
        
