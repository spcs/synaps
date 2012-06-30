# -*- coding:utf-8 -*-
# Copyright 2012 Samsung SDS
# All Rights Reserved

import datetime
import json

from pprint import pformat
from synaps import log as logging
from synaps import monitor
from synaps import exception
from synaps import utils

LOG = logging.getLogger(__name__)


class MonitorController(object):
    """
    MonitorController provides the critical dispatch between inbound API 
    calls through the endpoint and messages sent to the other nodes.
    """
    def __init__(self):
        self.monitor_api = monitor.API()

    def __str__(self):
        return 'MonitorController'

    def delete_alarms(self, context, alarm_names, project_id=None):
        if not (project_id and context.is_admin):
            project_id = context.project_id

        alarm_names = utils.extract_member_list(alarm_names)
        self.monitor_api.delete_alarms(project_id, alarm_names)            
        return {}

    def describe_alarm_history(self, context, alarm_name=None, end_date=None,
                               history_item_type=None, max_records=None,
                               next_token=None, start_date=None,
                               project_id=None):
        def to_alarm_history(v):
            ret = {
                'alarm_name': v['alarm_name'],
                'history_data': v['history_data'],
                'history_item_type': v['history_item_type'],
                'history_summary': v['history_summary'],
                'timestamp': utils.strtime(v['timestamp'],
                                           "%Y-%m-%dT%H:%M:%S.%fZ")
            }
            return ret
        
        if not (project_id and context.is_admin):
            project_id = context.project_id
            
        ret_dict = {}
        ret_histories = []
        next_token = None
        max_records = int(max_records) if max_records else 100        
            
        histories = self.monitor_api.describe_alarm_history(
            alarm_name=alarm_name, end_date=end_date,
            history_item_type=history_item_type,
            max_records=max_records, next_token=next_token,
            start_date=start_date, project_id=project_id
        )
        for k, v in histories:
            ret_histories.append(to_alarm_history(v))
            next_token = k
            
        ret_dict['describe_alarm_history_result'] = {'alarm_history_items': 
                                                     ret_histories}
        if next_token:
            ret_dict['describe_alarm_history_result']['next_token'] = \
                str(next_token)
        
        return ret_dict

    def describe_alarms(self, context, action_prefix=None,
                        alarm_name_prefix=None, alarm_names=None,
                        max_records=None, next_token=None, state_value=None,
                        project_id=None):
        def to_alarm(v):
            ret = {
                'action_enabled':v['action_enabled'],
                'alarm_actions':json.loads(v['alarm_actions']),
                'alarm_arn':v['alarm_arn'],
                'alarm_configuration_updated_timestamp':
                    utils.strtime(v['alarm_configuration_updated_timestamp'],
                                  "%Y-%m-%dT%H:%M:%S.%fZ"),
                'alarm_description':v['alarm_description'],
                'alarm_name':v['alarm_name'],
                'comparison_operator':v['comparison_operator'],
                'dimensions':
                    utils.dict_to_aws(json.loads(v['dimensions'])),
                'evaluation_period':v['evaluation_period'],
                'insufficient_data_actions':
                    json.loads(v['insufficient_data_actions']),
                'metric_name':v['metric_name'],
                'namespace':v['namespace'],
                'ok_actions':json.loads(v['ok_actions']),
                'period':v['period'],
                'project_id':v['project_id'],
                'state_reason':v['state_reason'],
                'state_reason_data':v['state_reason_data'],
                'state_updated_timestamp':
                    utils.strtime(v['state_updated_timestamp'],
                                  "%Y-%m-%dT%H:%M:%S.%fZ"),
                'state_value':v['state_value'],
                'statistic':v['statistic'],
                'threshold':v['threshold'],
                'unit':v['unit'],
            }
            return ret
        
        if not (project_id and context.is_admin):
            project_id = context.project_id
        
        max_records = int(max_records) if max_records else 100
        ret_dict = {}
        ret_alarms = []
        alarm_names = utils.extract_member_list(alarm_names) \
                      if alarm_names else None
        if alarm_names:
            if len(alarm_names) > 100:
                msg = "only 100 alarm names are allowed per request"
                raise exception.InvalidRequest(_(msg))        
            
        alarms = self.monitor_api.describe_alarms(project_id=project_id,
            action_prefix=action_prefix, alarm_name_prefix=alarm_name_prefix,
            alarm_names=alarm_names, max_records=max_records,
            next_token=next_token, state_value=state_value,
        )
        
        for k, v in alarms:
            ret_alarms.append(to_alarm(v))
            next_token = k
        
        ret_dict['describe_alarms_result'] = {'metric_alarms': ret_alarms}
        if next_token:
            ret_dict['describe_alarms_result']['next_token'] = str(next_token)
        
        return ret_dict
    
    def describe_alarms_for_metric(self, context, metric_name, namespace,
                                   dimensions=None, period=None,
                                   statistics=None, unit=None,
                                   project_id=None):
        if not (project_id and context.is_admin):
            project_id = context.project_id
        
        ret = {}
        # TODO: implement here
        return ret
    
    def disable_alarm_actions(self, context, alarm_names=None,
                              project_id=None):
        if not (project_id and context.is_admin):
            project_id = context.project_id
        
        ret = {}
        # TODO: implement here
        return ret
    
    def enable_alarm_actions(self, context, alarm_names=None,
                             project_id=None):
        if not (project_id and context.is_admin):
            project_id = context.project_id
        
        ret = {}
        # TODO: implement here
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
            k, v = metric
            return {
                'dimensions': utils.dict_to_aws(v['dimensions']),
                'metric_name': v['name'],
                'namespace': v['namespace']
            }
        
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
        
        d = utils.extract_member_dict(dimensions) if dimensions else {}
        
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
            dimensions=d,
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
        
        self.monitor_api.put_metric_data(project_id, namespace, metric_data,
                                         context.is_admin)
        return {}

    def set_alarm_state(self, context, alarm_name, state_reason, state_value,
                        state_reason_data=None):
        """
        Temporarily sets the state of an alarm. When the updated StateValue
        differs from the previous value, the action configured for the 
        appropriate state is invoked. This is not a permanent change. The next 
        periodic alarm check (in about a minute) will set the alarm to its 
        actual state. 
        """
        
        # TODO: implement here
        return {}
