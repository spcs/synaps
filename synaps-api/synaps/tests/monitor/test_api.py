# Copyright 2012 Samsung SDS
# All Rights Reserved

import unittest

import datetime
from synaps import utils
from synaps.context import RequestContext
from synaps.monitor.api import API

class TestApi(unittest.TestCase):
    def setUp(self):
        self.api = API()
#        self.context = RequestContext.from_dict({
#           'auth_token': None,
#           'is_admin': True,
#           'project_id': u'AKIAIUIUQBYNQ3G327RA',
#           'read_deleted': 'no',
#           'remote_address': '127.0.0.1',
#           'request_id': 'req-e03f36e0-5956-4114-8e32-fb7f3112c35c',
#           'roles': ['admin'],
#           'strategy': 'noauth',
#           'timestamp': '2012-03-23T06:34:40.320632',
#           'user_id': u'AKIAIUIUQBYNQ3G327RA'
#        })
        self.project_id = u'AKIAIUIUQBYNQ3G327RA'
        self.namespace = u'SPCS/NOVA'
        self.metric_data = {'member': {'1': 
            {'dimensions': 
                {'member': {'1': {'name': {'1': u'member1'},
                                  'value': {'1': u'value1'}}}},
            'metric_name': u'cpuutilization',
            'unit': u'Percent',
            'value': 10.2,
            'timestamp': utils.strtime()}}}

        self.api.put_metric_data(self.project_id, self.namespace,
                                 self.metric_data)
            
    def test_put_metric_data(self):
        ret = self.api.put_metric_data(self.project_id, self.namespace,
                                       self.metric_data)
        self.assertEqual(ret, {}) # success case
    
    def test_list_metric_data(self):
        dim = {u'member1':u'value1'}
        expected = {
            'project_id': u'AKIAIUIUQBYNQ3G327RA',
            'namespace': u'SPCS/NOVA',
            'dimensions': {u'member1':u'value1'},
            'name': u'cpuutilization'
        }

        metrics = self.api.list_metrics(self.project_id,
                                        namespace=self.namespace,
                                        dimensions=dim,
                                        metric_name=u'cpuutilization')
        
        for key, metric in metrics:
            self.assertEqual(metric, expected)
    
    def test_get_metric_statistics(self):
        dim = {u'member1':u'value1'}
        unit = None
        statistics = ['Average', 'Sum']
        metric_name = u'cpuutilization'
        end_time = utils.utcnow() + datetime.timedelta(seconds=60)
        start_time = utils.utcnow() - datetime.timedelta(hours=2)
        period = 60
        
        expected = {'Average': 10.2, 'Sum': 10.2}
        
        ret = self.api.get_metric_statistics(
            self.project_id, end_time=end_time, metric_name=metric_name,
            namespace=self.namespace, period=period, start_time=start_time,
            statistics=statistics, unit=None, dimensions=dim
        )
        
        self.assertEqual(ret[0][1]['Average'], 10.2)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
