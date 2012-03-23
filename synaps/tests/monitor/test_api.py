# Copyright 2012 Samsung SDS
# All Rights Reserved

import unittest
import datetime

from synaps import monitor
from synaps.context import RequestContext
from synaps.monitor.api import API, extract_member_dict, extract_member_list

class TestApi(unittest.TestCase):
    
    def setUp(self):
        self.api = API()
        self.context = RequestContext.from_dict({
           'auth_token': None,
           'is_admin': True,
           'project_id': u'AKIAIUIUQBYNQ3G327RA',
           'read_deleted': 'no',
           'remote_address': '127.0.0.1',
           'request_id': 'req-e03f36e0-5956-4114-8e32-fb7f3112c35c',
           'roles': ['admin'],
           'strategy': 'noauth',
           'timestamp': '2012-03-23T06:34:40.320632',
           'user_id': u'AKIAIUIUQBYNQ3G327RA'})
        self.namespace = u'SPCS/NOVA'
        self.metric_data = {'member': {'1': 
                                       {'dimensions': {'member': {'1':
                                                                  {'name': {'1': u'member1'},
                             'value': {'1': u'value1'}}}},
                        'metric_name': u'cpuutilization',
                        'statistic_values': {'maximum': 30,
                                             'minimum': 1,
                                             'sample_count': 100,
                                             'sum': 10000},
                        'unit': u'Percent'}}}
            
    def test_unpack_metric_data(self):
        self.api.put_metric_data(self.context, self.namespace,
                                 self.metric_data)
        
    def test_extract_member_list(self):
        # request test
        expected = [{'statistic_values': {'sum': 10000, 'minimum': 1,
                                          'maximum': 30, 'sample_count': 100},
                     'dimensions': {'member': {'1': {'name': {'1': u'member1'},
                                                     'value': {'1': u'value1'}}}},
                     'unit': u'Percent', 'metric_name': u'cpuutilization'}]
        
        real = extract_member_list(self.metric_data)
        self.assertEqual(real, expected)
        
        # test2
        input = {'member': {'1': 'something1',
                             '2': 'something2',
                             '3': 'something3'}}
        expected = ['something1', 'something2', 'something3']
        real = extract_member_list(input)
        
        self.assertEqual(real, expected)
    
        
        
    def test_extract_member_dict(self):
        input = {'member': {'1': {'name': {'1': u'member1'},
                                  'value': {'1': u'value1'}},
                            '2': {'name': {'1': u'member2'},
                                  'value': {'1': u'value2'}}}}

        expected = {u'member1': u'value1', u'member2': u'value2'}
        
        real = extract_member_dict(input)
        self.assertEqual(real, expected)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
