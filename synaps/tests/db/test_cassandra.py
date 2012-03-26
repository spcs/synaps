import unittest
import time
import pycassa

from synaps.db import Cassandra, MetricValueType


class TestCassandra(unittest.TestCase):
    def setUp(self):
#        Cassandra.reset()
        self.cass = Cassandra()

    def test_put_metric_data(self):
        project_id = "project_id"
        namespace = "AWS/EC2"
        metric_name = "CPU_Utilizaion"
        dimensions = {"instance-id":"i-00002f3e"}
        value = 102.321
        value2 = -82.21
        timestamp = time.time()
        unit = "Percent"
        
        self.cass.put_metric_data(project_id, namespace, metric_name,
                                  dimensions, value, unit)

        self.cass.put_metric_data(project_id, namespace, metric_name,
                                  dimensions, value2, unit)

        data = self.cass.get_metric_data(project_id, namespace, metric_name,
                                         dimensions, start=timestamp - 10,
                                         end=timestamp + 10)
        
        values = map(MetricValueType.unpack, data.values())
        self.assertTrue(value in values)
        self.assertTrue(value2 in values)              


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
