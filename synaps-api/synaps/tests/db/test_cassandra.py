# -*- coding:utf-8 -*-
# Copyright 2012 Samsung SDS
# All Rights Reserved

import unittest
import time
import datetime
import json
import pycassa
import uuid
from collections import OrderedDict

from synaps import flags
from synaps import log as logging
from synaps.db import Cassandra

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS

class TestCassandra(unittest.TestCase):
    """
    카산드라 DB를 테스트함.
    """
    
    def setUp(self):
        # initialize variables
        self.keyspace = "unittest"
        self.serverlist = FLAGS.get("cassandra_server_list")
        
        # initialize database
        Cassandra.syncdb(self.keyspace)
        self.cass = Cassandra(self.keyspace)
    
    def test_syncdb(self):
        """
        syncdb 결과 설정값 대로 keyspace가 DB에 있는지, 컬럼패밀리가 DB에 
        있는지 여부 확인.
        """
        self.cass.syncdb()
        
        manager = pycassa.SystemManager(server=self.serverlist[0])
        
        keyspaces = manager.list_keyspaces()
        column_families = manager.get_keyspace_column_families(self.keyspace)
        
        self.assertTrue(self.keyspace in keyspaces)
        self.assertEqual(set(column_families.keys()),
                         set(['Metric', 'StatArchive', 'MetricAlarm']))
    
    def test_restructed_stats(self):
        """
        """
        stats = {
            'Average': 
             OrderedDict([(datetime.datetime(1970, 1, 1, 0, 1), 11.0),
                          (datetime.datetime(1970, 1, 1, 0, 2), 11.0),
                          (datetime.datetime(1970, 1, 1, 0, 3), 11.0)]),
            'Sum': 
             OrderedDict([(datetime.datetime(1970, 1, 1, 0, 1), 44.0),
                          (datetime.datetime(1970, 1, 1, 0, 2), 44.0),
                          (datetime.datetime(1970, 1, 1, 0, 3), 44.0)])
        }
        
        expected = [
            (datetime.datetime(1970, 1, 1, 0, 1),
             {'Average': 11.0, 'Sum': 44.0}),
            (datetime.datetime(1970, 1, 1, 0, 2),
             {'Average': 11.0, 'Sum': 44.0}),
            (datetime.datetime(1970, 1, 1, 0, 3),
             {'Average': 11.0, 'Sum': 44.0}),
        ]

        self.assertEqual(expected, self.cass.restructed_stats(stats))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
