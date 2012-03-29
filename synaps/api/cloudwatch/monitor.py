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

    def put_metric_data(self, context, namespace, metric_data):
        """
        Publishes metric data points to Synaps. If specified metric does not
        exist Synaps creates the metric.
        """
        self.monitor_api.put_metric_data(context, namespace, metric_data)
        return {}

    def get_metric_statistics(self, context, **kwargs):
        return {}

    def list_metrics(self, context, next_token=None, dimensions=None,
                     metric_name=None, namespace=None):
        """
        Returns a list of valid metrics stored for the Synaps account owner. 
        Returned metrics can be used with get_metric_statics to obtain 
        statistical data for a given metric.
        """

        def to_aws_metric(metric):
            def to_aws_dimensions(dimensions):
                return [{'name':k, 'value':v} for k, v in dimensions.items()]
            
            k, v = metric
            ret = {}
            ret['dimensions'] = to_aws_dimensions(v['dimensions'])
            ret['metric_name'] = v['name']
            ret['namespace'] = v['namespace']
            return ret
        
        metrics = self.monitor_api.list_metrics(context, next_token, dimensions,
                                                metric_name, namespace)
        metrics = map(to_aws_metric, metrics)
        
        return {'ListMetricsResult': {'Metrics': metrics}}
