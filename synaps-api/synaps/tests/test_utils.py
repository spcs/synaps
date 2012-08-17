# Copyright 2012 Samsung SDS
# All Rights Reserved

import unittest
import datetime

from synaps import utils

class TestUtils(unittest.TestCase):

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
    
        
        
    def test_datetime_to_timestamp(self):
        epoch = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.assertEqual(0, utils.datetime_to_timestamp(epoch))
        
    def test_validate_international_phonenumber(self):
        number = '+82 311 2112'
        valid_set = (
            '+82 10 1234 5678',
            '+1 714 306 2014',
            '+82 2 1395 3134',
            '+292 19823476'
        )
        
        invalid_set = (
            '12321 123 1231 23',
            '02 123 4231'
        )
        
        for v in valid_set:
            ret = utils.validate_international_phonenumber(v)
            self.assertTrue(ret, "input value: %s" % v)

        for v in invalid_set:
            ret = utils.validate_international_phonenumber(v)
            self.assertFalse(ret, "input value: %s" % v)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
