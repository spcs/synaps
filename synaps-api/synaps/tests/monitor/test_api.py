# -*- coding:utf-8 -*-
# Copyright 2012 Samsung SDS
# All Rights Reserved

import unittest

from datetime import datetime, timedelta
from synaps import utils
from synaps.db import Cassandra
from synaps.context import RequestContext
from synaps.monitor.api import API, MetricMonitor
import uuid
import unittest

class FakeCassandra(object):
    def load_statistics(self, metric_key):
        return {
            'Average': {},
            'Minimum': {},
            'Maximum': {},
            'SampleCount': {},
            'Sum': {},
        }
    
    def insert_stat(self, metric_key, stat_dict):
        print metric_key, "inserted"
    

class TestMetricMonitor(unittest.TestCase):
    def setUp(self):
        metric_key = uuid.UUID('2e6637d7-eea4-4ee2-a91d-064762f3aae7')
        self.monitor = MetricMonitor(metric_key, FakeCassandra())

    def tearDown(self):
        pass

    def test_put_metric_data(self):
        now = datetime.utcnow()
        start = now - timedelta(hours=3)
        end = now
        timestamp = end - timedelta(minutes=3)
        timestamp_idx = timestamp.replace(second=0, microsecond=0)
        value = 50.2
        period = 5
        statistics = ['Average', 'SampleCount']
        unit = None

        before_stat = self.monitor.get_metric_statistics(
            timestamp_idx - timedelta(minutes=50), timestamp_idx, period,
            statistics, unit
        )

        for i in range(100):
            self.monitor.put_metric_data(
                timestamp - i * timedelta(minutes=0.24), float(i), unit
            )

        after_stat = self.monitor.get_metric_statistics(
            timestamp_idx - timedelta(minutes=50), timestamp_idx, period,
            statistics, unit
        )
        
        
class TestApi(unittest.TestCase):
    """
    Test the class, 'synaps.monitor.api.API'. 
    """
    def setUp(self):
        self.api = API()
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

    def test_put_metric_alarm(self):
        """
        API.put_metric_alarm 의 결과, Exception 없이 {} 이 반환 된 경우 PASS
        """
        # TODO: TBD
        metric = None
        alarm = None
#        ret = self.api.put_metric_alarm(metric, alarm)
#        self.assertEqual(ret, {})
        
    def test_put_metric_data(self):
        """
        API.put_metric_data 의 결과, Exception 없이 {} 이 반환 된 경우 PASS
        """
        ret = self.api.put_metric_data(self.project_id, self.namespace,
                                       self.metric_data)
        self.assertEqual(ret, {}) # success case
    
    def test_list_metric_data(self):
        """
        
        """
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

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
