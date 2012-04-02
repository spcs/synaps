# Copyright 2012 Samsung SDS
# All Rights Reserved

import unittest
import time
import pycassa

from synaps.db import Cassandra


class TestCassandra(unittest.TestCase):
    def setUp(self):
        Cassandra.reset()
        self.cass = Cassandra()
    
    def test_put_metric_data(self):
        # TODO: make test case
#        self.cass.put_metric_data(project_id, namespace, metric_name, 
#                                  dimensions, value, unit, timestamp)
        pass
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
