# Copyright 2012 Samsung SDS
# All Rights Reserved

import unittest
import datetime

from synaps import monitor
from synaps.context import RequestContext
from synaps.monitor.api import API

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
           'user_id': u'AKIAIUIUQBYNQ3G327RA'
        })
        self.namespace = u'SPCS/NOVA'
        self.metric_data = {'member': {'1': 
            {'dimensions': 
                {'member': {'1': {'name': {'1': u'member1'},
                                  'value': {'1': u'value1'}}}},
            'metric_name': u'cpuutilization',
            'unit': u'Percent',
            'value': 10.2 }}}
            
    def test_put_metric_data(self):
        ret = self.api.put_metric_data(self.context, self.namespace,
                                       self.metric_data)
        self.assertEqual(ret, {}) # success case
    
    def test_get_metric_statistics(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
