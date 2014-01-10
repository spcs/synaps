# -*- coding:utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright (c) 2012 Samsung SDS Co., LTD
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

from synaps.monitor.api import API
from synaps.utils import (validate_email, validate_international_phonenumber, 
                           validate_instance_action, 
                           validate_groupnotification_action)
import json

class Datapoint(object):
    """
    The Datapoint data type encapsulates the statistical data that Amazon 
    CloudWatch computes from metric data.
    
    Average    
        The average of metric values that correspond to the datapoint.
        Type: Double

    Maximum    
        The maximum of the metric value used for the datapoint.
        Type: Double

    Minimum    
        The minimum metric value used for the datapoint.
        Type: Double
    
    SampleCount    
        The number of metric values that contributed to the aggregate value of 
        this datapoint.
        Type: Double

    Sum    
        The sum of metric values used for the datapoint.
        Type: Double

    Timestamp    
        The time stamp used for the datapoint.
        Type: DateTime

    Unit    
        The standard unit used for the datapoint.
        Type: String
        
        Valid Values: Seconds | Microseconds | Milliseconds | Bytes | 
                      Kilobytes | Megabytes | Gigabytes | Terabytes | Bits | 
                      Kilobits | Megabits | Gigabits | Terabits | Percent | 
                      Count | Bytes/Second | Kilobytes/Second | 
                      Megabytes/Second | Gigabytes/Second | Terabytes/Second | 
                      Bits/Second | Kilobits/Second | Megabits/Second | 
                      Gigabits/Second | Terabits/Second | Count/Second | None
    """
    
class Dimension(object):
    """
    The Dimension data type further expands on the identity of a metric using 
    a Name, Value pair.

    For examples that use one or more dimensions, see PutMetricData.

    Name    
        The name of the dimension.
        Type: String
        Length constraints: Minimum length of 1. Maximum length of 255.

    Value    
        The value representing the dimension measurement
        Type: String
        Length constraints: Minimum length of 1. Maximum length of 255.
    """    
    
class DimensionFilter(object):
    """
    The DimensionFilter data type is used to filter ListMetrics results.

    Name    
        The dimension name to be matched.
        Type: String
        Length constraints: Minimum length of 1. Maximum length of 255.

    Value    
        The value of the dimension to be matched.
        Note: Specifying a Name without specifying a Value returns all values 
        associated with that Name.
        Type: String
        Length constraints: Minimum length of 1. Maximum length of 255.
    """

class GetMetricStatisticsResult(object):
    """
    The output for the GetMetricStatistics action.
    
    Datapoints    
        The datapoints for the specified metric.
        Type: Datapoint list

    Label    
        A label describing the specified metric.
        Type: String
    """

class ListMetricsResult(object):
    """
    The output for the ListMetrics action.

    Metrics    
        A list of metrics used to generate statistics for an AWS account.
        Type: Metric list

    NextToken    
        A string that marks the start of the next batch of returned results.
        Type: String
    """
    
class Metric(object):
    """
    The Metric data type contains information about a specific metric. If you 
    call ListMetrics, Amazon CloudWatch returns information contained by this 
    data type.

    The example in the Examples section publishes two metrics named buffers 
    and latency. Both metrics are in the examples namespace. Both metrics have 
    two dimensions, InstanceID and InstanceType.

    Dimensions    
        A list of dimensions associated with the metric.
        Type: Dimension list
        Length constraints: Minimum of 0 item(s) in the list. Maximum of 10 
        item(s) in the list.

    MetricName    
        The name of the metric.
        Type: String
        Length constraints: Minimum length of 1. Maximum length of 255.

    Namespace    
        The namespace of the metric.
        Type: String
        Length constraints: Minimum length of 1. Maximum length of 255.
    """
    def __init__(self, project_id=None, namespace=None, name=None,
                 dimensions=None):
        self.project_id = project_id
        self.name = name
        self.dimensions = dimensions

class MetricAlarm(object):
    OP_MAP = {'>=':'GreaterThanOrEqualToThreshold',
              '>':'GreaterThanThreshold',
              '<':'LessThanThreshold',
              '<=':'LessThanOrEqualToThreshold'}
    STATISTICS = ('SampleCount', 'Average', 'Sum', 'Minimum', 'Maximum')
    OP_VALUES = OP_MAP.values()
    
    def __init__(self, alarm_name, comparison_operator, evaluation_periods,
                 metric_name, namespace, period, statistic, threshold,
                 actions_enabled=False, alarm_actions=[], alarm_description="",
                 dimensions={}, insufficient_data_actions=[], ok_actions=[],
                 unit=""):
        def validate_actions(actions):
            assert (isinstance(actions, list))
            for a in actions:
                assert (validate_email(a) or 
                        validate_international_phonenumber(a) or
                        validate_instance_action(a) or
                        validate_groupnotification_action(a))
                
        assert (isinstance(actions_enabled, bool))
        self.actions_enabled = actions_enabled

        validate_actions(alarm_actions)
        self.alarm_actions = alarm_actions  
        
        validate_actions(insufficient_data_actions)
        self.insufficient_data_actions = insufficient_data_actions
        
        validate_actions(ok_actions)
        self.ok_actions = ok_actions

        assert (len(alarm_description) <= 255)
        self.alarm_description = alarm_description
        
        assert (len(alarm_name) <= 255)
        self.alarm_name = alarm_name
        
        assert (comparison_operator in self.OP_MAP.values())
        self.comparison_operator = comparison_operator
        
        assert (isinstance(dimensions, dict))
        self.dimensions = dimensions
        
        assert (isinstance(evaluation_periods, int))
        self.evaluation_periods = evaluation_periods
        
        assert (len(metric_name) <= 255)
        self.metric_name = metric_name 
        
        assert (len(namespace) <= 255)
        self.namespace = namespace
        

        assert (isinstance(period, int))
        self.period = period
        
        assert (statistic in self.STATISTICS)
        self.statistic = statistic
        
        self.threshold = threshold
        self.unit = unit
        
        self.alarm_arn = None
        self.alarm_configuration_updated_timestamp = None
        self.state_reason = None
        self.state_reason_data = None
        self.state_updated_timestamp = None
        self.state_value = None
        
    def to_columns(self):
        return {
            'actions_enabled': self.actions_enabled,
            'alarm_actions': json.dumps(self.alarm_actions),
            'alarm_arn': self.alarm_arn,
            'alarm_configuration_updated_timestamp': 
                self.alarm_configuration_updated_timestamp,
            'alarm_description': self.alarm_description,
            'alarm_name': self.alarm_name,
            'comparison_operator': self.comparison_operator,
            'dimensions':json.dumps(self.dimensions),
            'evaluation_periods':self.evaluation_periods,
            'insufficient_data_actions': \
                json.dumps(self.insufficient_data_actions),
            'metric_name':self.metric_name,
            'namespace':self.namespace,
            'ok_actions':json.dumps(self.ok_actions),
            'period':self.period,
            'statistic':self.statistic,
            'threshold':self.threshold,
            'unit':self.unit               
        }
    
    def __repr__(self):
        return "MetricAlarm:%s[%s(%s) %s %s]" % (self.alarm_name,
                                                 self.metric_name,
                                                 self.statistic,
                                                 self.comparison_operator,
                                                 self.threshold)
    

class MetricDatum(object):
    """
    The MetricDatum data type encapsulates the information sent with 
    PutMetricData to either create a new metric or add new values to be 
    aggregated into an existing metric.
    
    Dimensions    
        A list of dimensions associated with the metric.
        Type: Dimension list
        Length constraints: Minimum of 0 item(s) in the list. Maximum of 10 
        item(s) in the list.

    MetricName    
        The name of the metric.
        Type: String
        Length constraints: Minimum length of 1. Maximum length of 255.

    StatisticValues    
        A set of statistical values describing the metric.
        Type: StatisticSet

    Timestamp    
        The time stamp used for the metric. If not specified, the default 
        value is set to the time the metric data was received.
        Type: DateTime

    Unit    
        The unit of the metric.
        Type: String
        Valid Values: Seconds | Microseconds | Milliseconds | Bytes | 
                      Kilobytes | Megabytes | Gigabytes | Terabytes | Bits | 
                      Kilobits | Megabits | Gigabits | Terabits | Percent | 
                      Count | Bytes/Second | Kilobytes/Second | 
                      Megabytes/Second | Gigabytes/Second | Terabytes/Second | 
                      Bits/Second | Kilobits/Second | Megabits/Second | 
                      Gigabits/Second | Terabits/Second | Count/Second | None

    Value    
        The value for the metric.

        Important: Although the Value parameter accepts numbers of type 
        Double, Amazon CloudWatch truncates values with very large exponents. 
        Values with base-10 exponents greater than 126 (1 x 10^126) are 
        truncated. Likewise, values with base-10 exponents less than -130 
        (1 x 10^-130) are also truncated.

        Type: Double
    """
    
class StatisticSet(object):
    """
    The StatisticSet data type describes the StatisticValues component of 
    MetricDatum, and represents a set of statistics that describes a specific 
    metric.

    Maximum    
        The maximum value of the sample set.
        Type: Double

    Minimum    
        The minimum value of the sample set.
        Type: Double
    
    SampleCount    
        The number of samples used for the statistic set.
        Type: Double

    Sum    
        The sum of values for the sample set.
        Type: Double
    """
