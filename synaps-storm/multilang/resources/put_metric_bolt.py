#!/usr/bin/env python
# Copyright 2012 Samsung SDS

import pycassa
import os
import sys

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "synaps", "__init__.py")):
    sys.path.insert(0, possible_topdir)

import storm
import json
import uuid

from synaps import flags
from synaps import log as logging
from synaps import utils
from synaps.db import Cassandra, STAT_TYPE
from synaps.rpc import PUT_METRIC_DATA_MSG_ID

LOG = logging.getLogger(__name__)

class PutMetricBolt(storm.BasicBolt):
    def initialize(self, stormconf, context):
        self.cass = Cassandra()
        self.statistics = {}
    
    def update_statistics(self, metric_key, message):
        pass
    
    def load_or_create_statistics(self, metric_key, message):
        # TODO: load statistics data from cassandra
        
        
        # if no statistics data in cassandra, make initial data
        s = {}        
        for archive in Cassandra.ARCHIVE:
            for statistic in Cassandra.STATISTICS:
                s[(archive, statistic)] = {} 
    
    def process_put_metric_data_msg(self, metric_key, message):
        
        if self.statistics.has_key(metric_key):
            self.update_statistics(metric_key, message)
        else:
            self.load_or_create_statistics(metric_key, message)
            
        
        # update database
        self.cass.put_metric_data(
             project_id=message['project_id'],
             namespace=message['namespace'],
             metric_name=message['metric_name'],
             dimensions=message['dimensions'],
             value=message['value'],
             unit=message['unit'],
             timestamp=utils.parse_strtime(message['timestamp']),
             metric_key=metric_key
        )
        
        storm.log("write metric into database")
        
    def process(self, tup):
        metric_key = uuid.UUID(tup.values[0])
        message = json.loads(tup.values[1])
        message_id = message.get('message_id')
        
        if message_id == PUT_METRIC_DATA_MSG_ID:
            storm.log("process put_metric_data_msg (%s)" % message)
            self.process_put_metric_data_msg(metric_key, message)
        else:
            storm.log("unknown message")
            pass
            

if __name__ == "__main__":
    flags.FLAGS(sys.argv)
    utils.default_flagfile()
    logging.setup()
    PutMetricBolt().run()
