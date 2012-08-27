# Copyright (c) 2012 OpenStack, LLC
# Copyright 2012 SamsungSDS, Inc.
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


import unittest

from boto.ec2 import regioninfo
from boto.ec2.cloudwatch import CloudWatchConnection
from synaps.api.cloudwatch import monitor
from synaps import exception


class TestSynapsKeystoneContextMiddleware(unittest.TestCase):

    def setUp(self):
        self.mc = monitor.MonitorController()

    def tearDown(self):
        pass

    def test_check_alarm_name(self):
        alarm_name = "a" * 256
        self.assertRaises(exception.InvalidParameterValue,
                           self.mc.check_alarm_name, alarm_name)

    def test_check_alarm_names(self):
        alarm_names = ['test', 'test']
        self.assertTrue(self.mc.check_alarm_names(alarm_names))
        
        alarm_names = ['test'] * 101
        self.assertRaises(exception.InvalidRequest,
                          self.mc.check_alarm_names, alarm_names)

    def test_check_history_item_type(self):
        history_item_type = "It_will_Occur_an_error"
        self.assertRaises(exception.InvalidParameterValue,
                           self.mc.check_history_item_type, history_item_type)

    def test_check_action_prefix(self):
        action_prefix = "a" * 1025
        self.assertRaises(exception.InvalidParameterValue,
                           self.mc.check_action_prefix, action_prefix)

    def test_check_alarm_name_prefix(self):
        alarm_name_prefix = "a" * 256
        self.assertRaises(exception.InvalidParameterValue,
                           self.mc.check_alarm_name_prefix, alarm_name_prefix)

    def test_check_state_value(self):
        state_value = "It_will_Occur_an_error"
        self.assertRaises(exception.InvalidParameterValue,
                           self.mc.check_state_value, state_value)

    def test_check_dimensions(self):
        
        dimensions = ['OK', 'ALARM']
        self.assertTrue(self.mc.check_dimensions(dimensions))
        
        dimensions = ['OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK', 
                      'OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK', 
                      'OK', 'OK', 'OK', 'OK', 'OK', 'OK', 'OK']
        self.assertRaises(exception.InvalidParameterValue,
                          self.mc.check_dimensions, dimensions)
        
    def test_check_metric_name(self):
        metric_name = "a" * 256
        self.assertRaises(exception.InvalidParameterValue,
                           self.mc.check_metric_name, metric_name)

    def test_check_namespace(self):
        namespace = "a" * 256
        self.assertRaises(exception.InvalidParameterValue,
                           self.mc.check_namespace, namespace)

    def test_check_statistic(self):
        statistic = "It_will_Occur_an_error"
        self.assertRaises(exception.InvalidParameterValue,
                           self.mc.check_statistic, statistic)

    def test_check_statistics(self):
        statistics = ['ERROR', 'TEST']
        self.assertRaises(exception.InvalidParameterValue,
                          self.mc.check_statistics, statistics)
        
        statistics = ['Sum', 'Average']
        self.assertTrue(self.mc.check_statistics(statistics))
        
        statistics = ['Sum', 'Average', 'Sum', 'Sum', 'Sum', 'Sum']
        self.assertRaises(exception.InvalidParameterValue,
                          self.mc.check_statistics, statistics)
        


    def test_check_unit(self):
        unit = "It_will_Occur_an_error"
        self.assertRaises(exception.InvalidParameterValue,
                           self.mc.check_unit, unit)

    def test_check_alarm_description(self):
        alarm_description = "a" * 256
        self.assertRaises(exception.InvalidParameterValue,
                           self.mc.check_alarm_description,
                            alarm_description)

    def test_check_comparison_operator(self):
        comparison_operator = "It_will_Occur_an_error"
        self.assertRaises(exception.InvalidParameterValue,
                           self.mc.check_comparison_operator,
                            comparison_operator)

    def test_check_state_reason(self):
        state_reason = "a" * 1024
        self.assertRaises(exception.InvalidParameterValue,
                           self.mc.check_state_reason,
                            state_reason)

    def test_check_state_reason_data(self):
        state_reason_data = "a" * 4001
        self.assertRaises(exception.InvalidParameterValue,
                           self.mc.check_state_reason_data,
                            state_reason_data)

if __name__ == "__main__":
    unittest.main()
