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

    def delete_alrams(self, context, alarm_names, project_id=None):
        if not (project_id and context.is_admin):
            project_id = context.project_id
            
        ret = {}
        return ret

    def describe_alarm_history(self, context, alarm_name=None, end_date=None,
                               history_item_type=None, max_records=None,
                               next_token=None, start_date=None,
                               project_id=None):
        if not (project_id and context.is_admin):
            project_id = context.project_id
            
        ret = {}
        return ret

    def describe_alarms(self, context, action_prefix=None,
                        alarm_name_prefix=None, alarm_names=None,
                        max_records=None, next_token=None, state_value=None,
                        project_id=None):
        if not (project_id and context.is_admin):
            project_id = context.project_id
            
        ret = {}
        return ret
    
    def describe_alarms_for_metric(self, context, metric_name, namespace,
                                   dimensions=None, period=None,
                                   statistics=None, unit=None,
                                   project_id=None):
        if not (project_id and context.is_admin):
            project_id = context.project_id
        
        ret = {}
        return ret
    
    def disable_alarm_actions(self, context, alarm_names=None, 
                              project_id=None):
        if not (project_id and context.is_admin):
            project_id = context.project_id
        
        ret = {}
        return ret
    
    def enable_alarm_actions(self, context, alarm_names=None, 
                             project_id=None):
        if not (project_id and context.is_admin):
            project_id = context.project_id
        
        ret = {}
        return ret
    
    def get_metric_statistics(self, context, end_time, metric_name,
                              namespace, period, start_time, statistics,
                              unit=None, dimensions=None, project_id=None):
        """
        Gets statistics for the specified metric.
        """
        def stat_to_datapoint(stat):
            """
            단위 변경 및 형식 변경
            """
            timestamp, values = stat
            ret = {}
            ret['Timestamp'] = timestamp
            for statistic, value in values.iteritems():
                if statistic == "SampleCount":
                    ret['Unit'] = "Count"
                else:
                    ret['Unit'] = unit
                ret[statistic] = utils.to_unit(value, unit)
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
    
    def put_metric_alarm(self, context, alarm_name, comparison_operator,
                         evaluation_periods, metric_name, namespace, period,
                         statistic, threshold, alarm_actions=[],
                         insufficient_actions=[], ok_actions=[],
                         action_enabled=False, alarm_description="",
                         dimensions={}, unit="", project_id=None):
        """
        Create or updates an alarm and associates it with the specified
        SPCS Synaps metric.
        
        When this operation creates an alarm, the alarm state is immediately 
        set to INSUFFICIENT_DATA. The alarm is evaluated and its StateVale is 
        set appropriately. 
        """
        if not (project_id and context.is_admin):
            project_id = context.project_id
        
        metricalarm = monitor.MetricAlarm(
            alarm_name=alarm_name,
            comparison_operator=comparison_operator,
            evaluation_periods=evaluation_periods,
            metric_name=metric_name,
            namespace=namespace,
            period=period,
            statistic=statistic,
            threshold=threshold,
            action_enabled=action_enabled,
            alarm_actions=alarm_actions,
            alarm_description=alarm_description,
            dimensions=utils.extract_member_dict(dimensions),
            insufficient_data_actions=insufficient_actions,
            ok_actions=ok_actions,
            unit=unit
        )

        self.monitor_api.put_metric_alarm(project_id, metricalarm)
        
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

