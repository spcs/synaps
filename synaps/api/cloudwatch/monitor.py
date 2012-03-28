# Copyright 2012 Samsung SDS
# All Rights Reserved

from synaps import log as logging
from synaps import monitor
from synaps import exception

LOG = logging.getLogger(__name__)


class MonitorController(object):
    """ MonitorController provides the critical dispatch between
 inbound API calls through the endpoint and messages
 sent to the other nodes.
"""
    def __init__(self):
        self.monitor_api = monitor.API()

    def __str__(self):
        return 'MonitorController'

    def put_metric_data(self, context, namespace, metric_data, **kwargs):
        ret = self.monitor_api.put_metric_data(context, namespace,
                                               metric_data)
        return ret

    def get_metric_statistics(self, context, **kwargs):
        return {}

    def list_metrics(self, context, next_token=None, dimensions=None,
                     metric_name=None, namespace=None):
        
        def to_aws_dimensions(dimensions):
            """
            convert dictionary 
            
            >>> dimensions = {'name1': 'value1', 'name2': 'value2'}
            >>> to_aws_dimensions(dimensions)
            [{'name1': 'value1'}, {'name2', 'value2'}]
            """
            return [{'name':k, 'value':v} for k, v in dimensions.items()]
        
        def to_aws_metric(metric):
            k, v = metric
            ret = {}
            ret['dimensions'] = to_aws_dimensions(v['dimensions'])
            ret['metric_name'] = v['name']
            ret['namespace'] = v['namespace']
            return ret
        
        metrics = self.monitor_api.list_metrics(context, next_token, dimensions,
                                                metric_name, namespace)
        
        
        metrics = map(to_aws_metric, metrics)
        
        return {'ListMetricsResult': {'Metrics': metrics} }
