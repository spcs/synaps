# Copyright 2012 Samsung SDS
# All Rights Reserved

import unittest
import time
import datetime
import json

from collections import OrderedDict
from synaps.db import Cassandra

class TestCassandra(unittest.TestCase):
    def setUp(self):
        Cassandra.reset()
        self.cass = Cassandra()
    
    def test_put_metric_data(self):
        project_id = "test_project"
        namespace = "synapstest"
        metric_name = "test metric"
        dimensions = OrderedDict({'name':'value'})
        value1 = 10
        value2 = 12
        unit = "None"
        timestamp = time.time()

        timestamps = range(0, 1200, 30)
        self.assertEqual(len(timestamps), 40)

        for timestamp in timestamps:
            key = self.cass.put_metric_data(project_id, namespace,
                                            metric_name, dimensions, value1,
                                            unit, timestamp)
            key = self.cass.put_metric_data(project_id, namespace,
                                            metric_name, dimensions, value2,
                                            unit, timestamp + 10)
        
        metric = self.cass.cf_metric.get(key)
        self.assertEqual(metric['project_id'], project_id)
        self.assertEqual(metric['namespace'], namespace)
        self.assertEqual(json.loads(metric['dimensions']), dimensions)
        self.assertEqual(metric['name'], metric_name)
        
        archive = self.cass.cf_metric_archive.get(key, column_start=0,
                                                  column_finish=1200)
        self.assertEqual(len(archive), 80)
        self.assertEqual(archive.popitem()[1], value2)
        self.assertEqual(archive.popitem()[1], value1)
        
        utc_60 = datetime.datetime.utcfromtimestamp(60)
        
        count = self.cass.scf_stat_archive.get(
            key, super_column=(60, 'SampleCount'), columns=[utc_60]
        )
        self.assertEqual(count.popitem()[1], 4)

        sum_ = self.cass.scf_stat_archive.get(
            key, super_column=(60, 'Sum'), columns=[utc_60]
        )
        self.assertEqual(sum_.popitem()[1], (value1 + value2) * 2)
        
        avg = self.cass.scf_stat_archive.get(
            key, super_column=(60, 'Average'), columns=[utc_60]
        )
        self.assertEqual(avg.popitem()[1], (value1 + value2) / 2)

        minimum = self.cass.scf_stat_archive.get(
            key, super_column=(60, 'Minimum'), columns=[utc_60]
        )
        self.assertEqual(minimum.popitem()[1], min(value1, value2))

        maximum = self.cass.scf_stat_archive.get(
            key, super_column=(60, 'Maximum'), columns=[utc_60]
        )
        self.assertEqual(maximum.popitem()[1], max(value1, value2))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
