# Copyright 2012 Samsung SDS
# All Rights Reserved

import unittest
import datetime

from synaps import utils

class TestUtils(unittest.TestCase):

    def test_align_metrictime(self):
        actual = utils.align_metrictime(timestamp=90.0, resolution=60)
        self.assertEqual(actual, 120)

        actual = utils.align_metrictime(timestamp=100.0, resolution=60)
        self.assertEqual(actual, 120)

        actual = utils.align_metrictime(timestamp=60.0, resolution=60)
        self.assertEqual(actual, 120)

        actual = utils.align_metrictime(timestamp=120.0, resolution=60)
        self.assertEqual(actual, 180)

        actual = utils.align_metrictime(timestamp=125.0, resolution=60)
        self.assertEqual(actual, 180)

        actual = utils.align_metrictime(timestamp=149.0, resolution=60)
        self.assertEqual(actual, 180)

        actual = utils.align_metrictime(timestamp=150.0, resolution=60)
        self.assertEqual(actual, 180)

        actual = utils.align_metrictime(timestamp=170.1, resolution=60)
        self.assertEqual(actual, 180)

        
    def test_extract_member_list(self):
        metric_data = {'member': {'1': 
                          {'dimensions': 
                                {'member': 
                                 {'1': {'name': {'1': u'member1'},
                                        'value': {'1': u'value1'}}}},
                           'metric_name': u'cpuutilization',
                           'statistic_values': {'maximum': 30,
                                                'minimum': 1,
                                                'sample_count': 100,
                                                'sum': 10000},
                           'unit': u'Percent'}}}
        
        # request test
        expected = [{'statistic_values': {'sum': 10000, 'minimum': 1,
                                          'maximum': 30, 'sample_count': 100},
                     'dimensions': {'member': {'1': {'name': {'1': u'member1'},
                                                     'value': {'1': u'value1'}}}},
                     'unit': u'Percent', 'metric_name': u'cpuutilization'}]
        
        real = utils.extract_member_list(metric_data)
        self.assertEqual(real, expected)
        
        # test2
        input = {'member': {'1': 'something1',
                             '2': 'something2',
                             '3': 'something3'}}
        expected = ['something1', 'something2', 'something3']
        real = utils.extract_member_list(input)
        
        self.assertEqual(sorted(real), sorted(expected))
    
        
        
    def test_extract_member_dict(self):
        input = {'member': {'1': {'name': {'1': u'member1'},
                                  'value': {'1': u'value1'}},
                            '2': {'name': {'1': u'member2'},
                                  'value': {'1': u'value2'}}}}

        expected = {u'member1': u'value1', u'member2': u'value2'}
        
        real = utils.extract_member_dict(input)
        self.assertEqual(real, expected)
        
    def test_datetime_to_timestamp(self):
        epoch = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.assertEqual(0, utils.datetime_to_timestamp(epoch)) 


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
