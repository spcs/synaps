# Copyright 2012 Samsung SDS
# All Rights Reserved

import datetime

from synaps import log as logging
from synaps import monitor
from synaps import exception
from synaps import utils

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
    
    def put_metric_alarm(self, context, name, operator, evaluation_period, 
                         metric_name, namespace, period, statistic, threshold,                          
                         alarm_actions=None, insufficient_action=None,
                         ok_action=None, action_enabled=None, 
                         description=None, dimensions=None, unit=None, 
                         project_id=None):
        """
        Create or updates an alarm and associates it with the specified
        SPCS Synaps metric. 
        
        When this operation creates an alarm, the alarm state is immediately 
        set to INSUFFICIENT_DATA. The alarm is evaluated and its StateVale is 
        set appropriately. 
        """
        if not (project_id and context.is_admin):
            project_id = context.project_id
        
        metric = None
        alarm = None
            
        self.monitor_api.put_metric_alarm(metric, alarm)
        
        return {}


    def put_metric_data(self, context, namespace, metric_data,
                        project_id=None):
        """
        Publishes metric data points to Synaps. If specified metric does not
        exist, Synaps creates the metric.
        """
        if not (project_id and context.is_admin):
            project_id = context.project_id
        
        self.monitor_api.put_metric_data(project_id, namespace,
                                         metric_data)
        return {}

    def get_metric_statistics(self, context, end_time, metric_name,
                              namespace, period, start_time, statistics,
                              unit="None", dimensions=None, project_id=None):
        """
        Gets statistics for the specified metric.
        """
        def stat_to_datapoint(stat):
            timestamp, values = stat
            ret = {}
            ret['Timestamp'] = timestamp
            for statistic, value in values.items():
                ret[statistic] = value
            ret['Unit'] = 'None'
            return ret
                
        if not (project_id and context.is_admin):
            project_id = context.project_id
        end_time = utils.parse_strtime(end_time)
        start_time = utils.parse_strtime(start_time)
        dimensions = utils.extract_member_dict(dimensions) \
                     if dimensions else None
        statistics = utils.extract_member_list(statistics)
        stats = self.monitor_api.get_metric_statistics(project_id, end_time,
                                                       metric_name, namespace,
                                                       period, start_time,
                                                       statistics, unit,
                                                       dimensions)
        
        datapoints = map(stat_to_datapoint, stats)
        label = metric_name
        
        return {'GetMetricStatisticsResult': {'Datapoints': datapoints,
                                              'Label': label}}

    def list_metrics(self, context, next_token=None, dimensions=None,
                     metric_name=None, namespace=None, project_id=None):
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
        
        if not (project_id and context.is_admin):
            project_id = context.project_id
        dimensions = utils.extract_member_dict(dimensions) \
                     if dimensions else None
        metrics = self.monitor_api.list_metrics(project_id, next_token,
                                                dimensions, metric_name,
                                                namespace)
        metrics = map(to_aws_metric, metrics)
        
        return {'ListMetricsResult': {'Metrics': metrics}}
