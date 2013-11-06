# -*- coding:utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright (c) 2012 Samsung SDS, Co., LTD
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import datetime
import json
import uuid

from synaps import log as logging
from synaps import monitor
from synaps import exception
from synaps import flags
from synaps import utils
from synaps.exception import InvalidParameterValue
from synaps import db

from novaclient.exceptions import NotFound 

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS    

def to_alarm(v):
    ret = {
        'actions_enabled': v['actions_enabled'],
        'alarm_actions': json.loads(v['alarm_actions']),
        'alarm_arn': v['alarm_arn'],
        'alarm_configuration_updated_timestamp':
            utils.strtime_trunk(v['alarm_configuration_updated_timestamp']),
        'alarm_description': v['alarm_description'],
        'alarm_name': v['alarm_name'],
        'comparison_operator': v['comparison_operator'],
        'dimensions':
            utils.dict_to_aws(json.loads(v['dimensions'])),
        'evaluation_periods': v['evaluation_periods'],
        'insufficient_data_actions':
            json.loads(v['insufficient_data_actions']),
        'metric_name': v['metric_name'],
        'namespace': v['namespace'],
        'OK_actions': json.loads(v['ok_actions']),
        'period': v['period'],
        'project_id': v['project_id'],
        'state_reason': v['state_reason'],
        'state_reason_data': v['state_reason_data'],
        'state_updated_timestamp':
            utils.strtime_trunk(v['state_updated_timestamp']),
        'state_value': v['state_value'],
        'statistic': v['statistic'],
        'threshold': v['threshold'],
        'unit': v['unit'],
    }
    return ret


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

        self.check_alarm_names(alarm_names)
        self._check_admin_alarm(alarm_names, context.is_admin)

        alarm_names = utils.extract_member_list(alarm_names)
        self.monitor_api.delete_alarms(context, project_id, alarm_names)
        return {}

    def describe_alarm_history(self, context, alarm_name=None, end_date=None,
                               history_item_type=None, max_records=100,
                               next_token=None, start_date=None,
                               project_id=None):
        def to_alarm_history(v):
            ret = {
                'alarm_name': v['alarm_name'],
                'history_data': v['history_data'],
                'history_item_type': v['history_item_type'],
                'history_summary': v['history_summary'],
                'timestamp': utils.strtime_trunk(v['timestamp'])
            }
            return ret

        if not (project_id and context.is_admin):
            project_id = context.project_id

        self.check_alarm_name(alarm_name)
        self.check_history_item_type(history_item_type)
        self.check_next_token(next_token)
        
        ret_dict = {}
        ret_histories = []
        end_date = utils.parse_strtime(end_date) if end_date else end_date
        start_date = utils.parse_strtime(start_date) \
                     if start_date else start_date

        LOG.debug("request to database for alarm history")        
        histories = self.monitor_api.describe_alarm_history(
            alarm_name=alarm_name, end_date=end_date,
            history_item_type=history_item_type,
            max_records=max_records + 1, next_token=next_token,
            start_date=start_date, project_id=project_id
        )
        
        LOG.debug("convert to list")
        histories = list(histories)
        LOG.debug("to list %d", len(histories))
        
        LOG.debug("start to read histories")
        for i, (k, v) in enumerate(histories):
            if i >= max_records:
                next_token = k
                LOG.debug("reached to the number of max records")
                break
            ret_histories.append(to_alarm_history(v))
            LOG.debug("not reached to the number of max records")
        else:
            next_token = None
            
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
        
        if not (project_id and context.is_admin):
            project_id = context.project_id
        
        max_records = int(max_records) if max_records else 100
        ret_dict = {}
        ret_alarms = []
        alarm_names = utils.extract_member_list(alarm_names) \
                      if alarm_names else None
        
        self.check_action_prefix(action_prefix)
        if alarm_names:
            self.check_alarm_names(alarm_names)
        else:
            self.check_alarm_name_prefix(alarm_name_prefix)
        self.check_state_value(state_value)
        self.check_next_token(next_token)   

        alarms = self.monitor_api.describe_alarms(project_id=project_id,
            action_prefix=action_prefix, alarm_name_prefix=alarm_name_prefix,
            alarm_names=alarm_names, max_records=max_records + 1,
            next_token=next_token, state_value=state_value,
        )
        
        for i, (k, v) in enumerate(alarms):
            if i >= max_records:
                next_token = k
                break
            ret_alarms.append(to_alarm(v))
        else:
            next_token = None
        
        ret_dict['describe_alarms_result'] = {'metric_alarms': ret_alarms}
        if next_token:
            ret_dict['describe_alarms_result']['next_token'] = str(next_token)
        
        return ret_dict
    
    def describe_alarms_for_metric(self, context, namespace, metric_name,
                                   dimensions=None, period=None,
                                   statistic=None, unit=None, project_id=None):
        if not (project_id and context.is_admin):
            project_id = context.project_id
               

        ret_dict = {}
        ret_alarms = []
        dimensions = utils.extract_member_dict(dimensions)
        
        self.check_dimensions(dimensions)
        self.check_metric_name(metric_name)
        self.check_namespace(namespace)
        self.check_statistic(statistic)
        self.check_unit(unit)
        
        alarms = self.monitor_api.describe_alarms_for_metric(
            project_id=project_id, namespace=namespace,
            metric_name=metric_name, dimensions=dimensions, period=period,
            statistic=statistic, unit=unit
        )
        
        for k, v in alarms:
            ret_alarms.append(to_alarm(v))

        ret_dict['describe_alarms_for_metric_result'] = {'metric_alarms': 
                                                         ret_alarms}
        
        return ret_dict
            
    def disable_alarm_actions(self, context, alarm_names=None,
                              project_id=None):
        if not (project_id and context.is_admin):
            project_id = context.project_id
        
        self.check_alarm_names(alarm_names)
        self._check_admin_alarm(alarm_names, context.is_admin)
        
        alarm_names = utils.extract_member_list(alarm_names)
        self.monitor_api.set_alarm_actions(context, project_id, alarm_names,
                                           False)
        return {}        
    
    def enable_alarm_actions(self, context, alarm_names=None,
                             project_id=None):
        if not (project_id and context.is_admin):
            project_id = context.project_id
        
        self.check_alarm_names(alarm_names)
        self._check_admin_alarm(alarm_names, context.is_admin)

        alarm_names = utils.extract_member_list(alarm_names)
        self.monitor_api.set_alarm_actions(context, project_id, alarm_names,
                                           True)
        return {}      
    
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
                    ret[statistic] = value
                else:
                    ret['Unit'] = (unit if unit != 'None' else None)
                    ret[statistic] = utils.to_unit(value, unit)
                    
            return ret

        if not (project_id and context.is_admin):
            project_id = context.project_id
        end_time = utils.parse_strtime(end_time)
        start_time = utils.parse_strtime(start_time)
        dimensions = utils.extract_member_dict(dimensions)
        statistics = utils.extract_member_list(statistics)
        
        self.check_dimensions(dimensions)
        self.check_metric_name(metric_name)
        self.check_namespace(namespace)
        self.check_statistics(statistics)
        self.check_unit(unit)
        self._validate_period(period)
        self.validate_get_metric_statistics(start_time, end_time, period)
        
        stats, unit = self.monitor_api.get_metric_statistics(
                                                       project_id, end_time,
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
        dimensions = utils.extract_member_dict(dimensions)
        self._check_dimension_filter(dimensions)
        self.check_metric_name(metric_name)
        self.check_namespace(namespace)  
        self.check_next_token(next_token)

        metrics, next_token = self.monitor_api.list_metrics(project_id, 
                            next_token, dimensions, metric_name, namespace)
       
        metrics = map(to_aws_metric, metrics)

        list_metrics_result = {'Metrics': metrics}
        if next_token:
            list_metrics_result['NextToken'] = next_token
        
        return {'ListMetricsResult': list_metrics_result}


    def put_metric_alarm(self, context, alarm_name, comparison_operator,
                         evaluation_periods, metric_name, namespace, period,
                         statistic, threshold, alarm_actions=[],
                         insufficient_data_actions=[], ok_actions=[],
                         actions_enabled=True, alarm_description="",
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
        
        d = utils.extract_member_dict(dimensions)
        alarm_actions = utils.extract_member_list(alarm_actions)
        insufficient_data_actions = \
            utils.extract_member_list(insufficient_data_actions)
        ok_actions = utils.extract_member_list(ok_actions)
        
        self.check_alarm_description(alarm_description)
        self.check_alarm_name(alarm_name)
        self._check_admin_alarm([alarm_name], context.is_admin)
        self.check_comparison_operator(comparison_operator)
        self.check_dimensions(dimensions)
        self.check_metric_name(metric_name)
        self.check_namespace(namespace)
        self.check_statistic(statistic)
        self.check_unit(unit)
        self._validate_period(period)
        self._validate_evaluation_periods(evaluation_periods)
        self.validate_put_metric_alarm(period, evaluation_periods)   
        self._validate_instanceaction(ok_actions, project_id, context)
        self._validate_instanceaction(insufficient_data_actions, project_id,
                                      context)
        self._validate_instanceaction(alarm_actions, project_id, context)
        
        try:
            metricalarm = monitor.MetricAlarm(
                alarm_name=alarm_name,
                comparison_operator=comparison_operator,
                evaluation_periods=evaluation_periods,
                metric_name=metric_name,
                namespace=namespace,
                period=period,
                statistic=statistic,
                threshold=threshold,
                actions_enabled=actions_enabled,
                alarm_actions=alarm_actions,
                alarm_description=alarm_description,
                dimensions=d,
                insufficient_data_actions=insufficient_data_actions,
                ok_actions=ok_actions,
                unit=unit
            )
        except AssertionError as e:
            LOG.exception(e)
            err = "Unsuitable MetricAlarm Value(%s)" % str(e)
            raise InvalidParameterValue(err)

        self.monitor_api.put_metric_alarm(context, project_id, metricalarm)
        
        return {}


    def put_metric_data(self, context, namespace, metric_data,
                        project_id=None):
        """
        Publishes metric data points to Synaps. If specified metric does not
        exist, Synaps creates the metric.
        """
        def parse_metric_data(metric):
            try:
                dimensions_ = metric.get('dimensions', {})
                dimensions = utils.extract_member_dict(dimensions_)
            except KeyError:
                err = "Unsuitable Dimensions Value - %s" % str(dimensions_)
                raise InvalidParameterValue(err)
        
            metric_name = metric.get('metric_name')
            unit = metric.get('unit', 'None')
            value = metric.get('value')
            req_timestamp = metric.get('timestamp')
            timestamp = req_timestamp if req_timestamp \
                        else utils.strtime(utils.utcnow())
            timebound = (datetime.datetime.utcnow() - 
                         datetime.timedelta(
                                        seconds=FLAGS.get('statistics_ttl')))
            
            if utils.parse_strtime(timestamp) < timebound:
                err = "Stale metric data - %s" % timestamp
                raise InvalidParameterValue(err)
            
            self.check_metric_name(metric_name)
            self.check_unit(unit)
            
            return metric_name, dimensions, value, unit, timestamp 
                
        
        if not (project_id and context.is_admin):
            project_id = context.project_id
        
        self.check_namespace(namespace)
        
        metrics = [parse_metric_data(metric) for metric 
                   in utils.extract_member_list(metric_data)]

        for metric in metrics:
            metric_name, dimensions, value, unit, timestamp = metric
            self.monitor_api.put_metric_data(context,
                                             project_id=project_id,
                                             namespace=namespace,
                                             metric_name=metric_name,
                                             dimensions=dimensions,
                                             value=value,
                                             unit=unit,
                                             timestamp=timestamp,
                                             is_admin=context.is_admin)           
        return {}

    def set_alarm_state(self, context, alarm_name, state_reason, state_value,
                        state_reason_data=None, project_id=None):
        """
        Temporarily sets the state of an alarm. When the updated StateValue
        differs from the previous value, the action configured for the 
        appropriate state is invoked. This is not a permanent change. The next 
        periodic alarm check (in about a minute) will set the alarm to its 
        actual state. 
        """
        if not (project_id and context.is_admin):
            project_id = context.project_id
        
        self.check_alarm_name(alarm_name)
        self._check_admin_alarm([alarm_name], context.is_admin)
        self.check_state_reason(state_reason)
        self.check_state_reason_data(state_reason_data)
        self.check_state_value(state_value)

        self.monitor_api.set_alarm_state(context, project_id, alarm_name,
                                         state_reason, state_value,
                                         state_reason_data)
        return {}

    def check_alarm_name(self, alarm_name):        

        if unicode(alarm_name) and unicode(alarm_name) != u"None":
            try:
                if (not (0 < len(alarm_name) <= 255)):
                    err = "The length of Alarm name is 1~255."
                    raise exception.InvalidParameterValue(err)
                
            except TypeError:
                err = "Alarm name should not be consist only of numbers. "
                raise exception.InvalidParameterValue(err)
        
        return True 
    
    def check_alarm_names(self, alarm_names):
        if alarm_names:
            if len(alarm_names) > 100:
                msg = "only 100 alarm names are allowed per request"
                raise exception.InvalidRequest(_(msg))
        
        return True 

    
    def check_history_item_type(self, history_item_type):
        
        history_item_sample = ['ConfigurationUpdate', 'StateUpdate', 'Action']
        if history_item_type and (history_item_type not in history_item_sample):
            err = "Unsuitable History Item Type Value"
            raise exception.InvalidParameterValue(err)
        
        return True 

    
    def check_action_prefix(self, action_prefix):
    
        if unicode(action_prefix) and unicode(action_prefix) != u"None":
            try:
                if (not (0 < len(action_prefix) <= 1024)):
                    err = "The length of Action Prefix is 1~1024."
                    raise exception.InvalidParameterValue(err)
                
            except TypeError:
                err = "Action Prefix should not be consist only of numbers. "
                raise exception.InvalidParameterValue(err)
        
        return True
     
    def check_alarm_name_prefix(self, alarm_name_prefix):
    
        if unicode(alarm_name_prefix) and unicode(alarm_name_prefix) != u"None":
            try:
                if (not (0 < len(alarm_name_prefix) <= 255)):
                    err = "The length of Alarm Name Prefix is 1~255."
                    raise exception.InvalidParameterValue(err)
                
            except TypeError:
                err = "Alarm Name Prefix should not be consist only of numbers. "
                raise exception.InvalidParameterValue(err)
        
        return True

    
    def check_state_value(self, state_value):
        state_value_sample = ['OK', 'ALARM', 'INSUFFICIENT_DATA']
        if state_value and (state_value not in state_value_sample):
            err = "Unsuitable State Value"
            raise exception.InvalidParameterValue(err)
            
        return True   

    
    def _check_dimension_filter(self, dimensions):
        if dimensions and (not (0 <= len(dimensions) <= 10)):
            err = "The length of Dimensions is 0~10."
            raise exception.InvalidParameterValue(err)
        
        return True 
    
    def check_dimensions(self, dimensions):
        if dimensions and (not (0 <= len(dimensions) <= 10)):
            err = "The length of Dimensions is 0~10."
            raise exception.InvalidParameterValue(err)
        
        return True 
    
    def check_metric_name(self, metric_name):
        
        if unicode(metric_name) and unicode(metric_name) != u"None":
            try:
                if (not (0 < len(metric_name) <= 255)):
                    err = "The length of Metric Name is 1~255."
                    raise exception.InvalidParameterValue(err)
                
            except TypeError:
                err = "Metric Name should not be consist only of numbers. " + unicode(metric_name) + " " + u"None"
                raise exception.InvalidParameterValue(err)
        
        return True 
    
    def check_namespace(self, namespace):

        if unicode(namespace) and unicode(namespace) != u"None":
            try:
                if (not (0 < len(namespace) <= 255)):
                    err = "The length of Namespace is 1~255."
                    raise exception.InvalidParameterValue(err)
                
            except TypeError:
                err = "Namespace should not be consist only of numbers. "
                raise exception.InvalidParameterValue(err)
        
        return True 
    
    def check_next_token(self, next_token):
        if not next_token:
            return True
        else:
            next_token = next_token.replace(' ', '')
            try:
                uuid.UUID(next_token)
            except ValueError:
                err = "badly formed nextToken(%s)" % next_token
                raise exception.InvalidParameterValue(err)
        
        return True
    
    def check_statistic(self, statistic):
        statistic_sample = db.Cassandra.STATISTICS
        if statistic and (statistic not in statistic_sample):
            err = "Unsuitable Statistic Value %s" % statistic
            raise exception.InvalidParameterValue(err)
        
        return True 
    
    def check_statistics(self, statistics):
        statistic_sample = db.Cassandra.STATISTICS
        if statistics:
            if (not (0 < len(statistics) <= 5)):
                err = "The length of Namespace is 1~5."
                raise exception.InvalidParameterValue(err)
            else:
                for statistic in statistics:
                    if statistic and (statistic not in statistic_sample):
                        err = "Unsuitable Statistic Value %s" % str(statistic)
                        raise exception.InvalidParameterValue(err)
        
        return True
                    
    def check_unit(self, unit):
        unit_sample = utils.UNITS
        if unit and (unit not in unit_sample):
            err = "Unsuitable Unit Value"
            raise exception.InvalidParameterValue(err)
        
        return True
    
    def check_alarm_description(self, alarm_description):

        if unicode(alarm_description) and unicode(alarm_description) != u"None":
            try:
                if (not (0 < len(alarm_description) <= 255)):
                    err = "The length of Alarm Description is 1~255."
                    raise exception.InvalidParameterValue(err)
                
            except TypeError:
                err = "Alarm Description should not be consist only of numbers. "
                raise exception.InvalidParameterValue(err)
        
        return True      
       
    def check_comparison_operator(self, comparison_operator):
        comparison_operator_sample = ['GreaterThanOrEqualToThreshold',
                                      'GreaterThanThreshold',
                                      'LessThanThreshold',
                                      'LessThanOrEqualToThreshold']
        if comparison_operator and (comparison_operator not in 
                                    comparison_operator_sample):
            err = "Unsuitable Comparison Operator Value"
            raise exception.InvalidParameterValue(err)
        
        return True    
    
    def check_state_reason(self, state_reason):
  
    
        if unicode(state_reason) and unicode(state_reason) != u"None":
            try:
                if (not (0 < len(state_reason) <= 1023)):
                    err = "The length of State Reason is 1~1023."
                    raise exception.InvalidParameterValue(err)
                
            except TypeError:
                err = "State Reason should not be consist only of numbers. " + str(state_reason)
                raise exception.InvalidParameterValue(err)
        
        return True      
        
    def check_state_reason_data(self, state_reason_data):
    
        if unicode(state_reason_data) and unicode(state_reason_data) != u"None":
            try:
                if (not (0 < len(state_reason_data) <= 4000)):
                    err = "The length of State Reason Data is 1~4000."
                    raise exception.InvalidParameterValue(err)
                
            except TypeError:
                err = "State Reason Data should not be consist only of numbers. " + str(state_reason_data)
                raise exception.InvalidParameterValue(err)
        
        return True 
    
    def _validate_period(self, period):
        if (not 0 < int(period) <= (60 * 60 * 24)):
            err = "The length of Period is 1~86400. (24 hours)"
            raise exception.InvalidParameterValue(err)
        
        if (not int(period) % 60 == 0):
            err = "Period is must be multiple of 60."
            raise exception.InvalidParameterValue(err)
            
        return True
    
    def _validate_evaluation_periods(self, evaluation_periods):
        if evaluation_periods and (not 0 < int(evaluation_periods) <= 1440):
            err = "Evaluation Periods should be in range of 1~1440."
            raise exception.InvalidParameterValue(err)

    def validate_put_metric_alarm(self, period, evaluation_periods):
        self._validate_period(period)
        self._validate_evaluation_periods(evaluation_periods)
        
        if (int(period) * int(evaluation_periods) > (60 * 60 * 24)):
            err = "Period * EvaluationPeriods should not exceed 86400(24 hours)"
            raise exception.InvalidParameterValue(err)

    def validate_get_metric_statistics(self, start_time, end_time, period):
        minute = datetime.timedelta(minutes=1)
        max_query_period = FLAGS.get('max_query_period_minutes') * minute
        max_query_datapoints = FLAGS.get('max_query_datapoints')
        period_diff = end_time - start_time
        if not (datetime.timedelta(0) <= period_diff <= max_query_period):
            err = "Difference between start_time and end_time should be "\
                  "lesser than %s" % max_query_period  
            raise exception.InvalidParameterValue(err)
        
        queried_datapoints = (period_diff.total_seconds() / (int(period)))
        if queried_datapoints > max_query_datapoints:
            err = "Requested too many datapoints (%d). "\
                  "Limitation is %s datapoints" % (queried_datapoints,
                                                   max_query_datapoints) 
            raise exception.InvalidParameterValue(err)
        
    def _validate_instanceaction(self, actions, project_id, context):
        instanceactions = [action for action in actions 
                           if utils.validate_instance_action(action)]
        parsed = [utils.parse_instance_action(a) for a in instanceactions]
        nc = utils.get_python_novaclient()
        err = "Server is not found"
        
        for action_type, vm_uuid in parsed:
            try:
                server = nc.servers.get(vm_uuid)
            except NotFound:
                raise exception.InvalidParameterValue(err)

            if not context.is_admin and server.tenant_id != project_id:
                raise exception.InvalidParameterValue(err)
        
    def _check_admin_alarm(self, alarms, is_admin):
        if isinstance(alarms, (str, unicode)):
            alarms = [alarms]
        
        for alarm in alarms:
            if alarm.startswith("SPCS/") and not is_admin:
                raise exception.AdminRequired() 
                

