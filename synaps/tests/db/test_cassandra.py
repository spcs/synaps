'''
Created on Mar 26, 2012

@author: june
'''
import unittest
import time
from synaps.db import Cassandra

class TestCassandra(unittest.TestCase):
    def setUp(self):
        Cassandra.reset()
        self.cass = Cassandra()

    def test_put_metric_data(self):
        project_id = "project_id"
        namespace = "AWS/EC2"
        metric_name = "CPU_Utilizaion"
        dimensions = {"instance-id":"i-00002f3e"}
        value = 10.4
        timestamp = time.time()
        unit = "Percent"
        
        self.cass.put_metric(project_id, namespace, metric_name, dimensions,
                             value, timestamp, unit)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
