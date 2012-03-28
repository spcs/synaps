# Copyright 2012 Samsung SDS
# All Rights Reserved

import unittest
import time
import pycassa

from synaps.db import Cassandra, MetricValueType


class TestCassandra(unittest.TestCase):
    def setUp(self):
        Cassandra.reset()
        
        self.n_metric = 10
        self.cass = Cassandra()
        self.project_id = project_id = "project_id"
        self.namespace = namespace = "TEST/CASSANDRA"
        dimensions = {"instance-id":"i-00002f3e"}
        unit = "Percent"

        for j in range(self.n_metric):
            metric_name = "CPU_Utilizaion_%d" % j
            now = int(time.time()) 
            for i in range(10):
                timestamp = now - (now % 60) - i * 60
                value = i * 10.2 * (-1) ** i
                self.cass.put_metric_data(project_id, namespace, metric_name,
                                          dimensions, value, unit)
        

    def test_put_metric_data(self):
        project_id = "project_id"
        namespace = "AWS/EC2"
        metric_name = "CPU_Utilizaion_2"
        dimensions = {"instance-id":u"i-00002f3e"}
        value = 82.21
        timestamp = time.time()
        unit = "Percent"
        
        self.cass.put_metric_data(project_id, namespace, metric_name,
                                  dimensions, value, unit)

        data = self.cass.get_metric_data(project_id, namespace, metric_name,
                                         dimensions, start=timestamp - 10,
                                         end=timestamp + 10)
        
        lv = MetricValueType.pack(value)
        rv = data.values()
        
        self.assertTrue(lv in rv)
    
    def test_list_metrics(self):
        metrics = self.cass.list_metrics(self.project_id)
        self.assertEqual(len(metrics), self.n_metric)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
