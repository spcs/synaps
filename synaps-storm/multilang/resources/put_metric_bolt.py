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
from synaps.db import Cassandra

class PutMetricBolt(storm.BasicBolt):
    def initialize(self, stormconf, context):
        self.cass = Cassandra()
        self.metrics = {}
    
    def process(self, tup):
        metric_key = uuid.UUID(tup.values[0])
        message = json.loads(tup.values[1])
        
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

if __name__ == "__main__":
    flags.FLAGS(sys.argv)
    utils.default_flagfile()
    logging.setup()
    PutMetricBolt().run()
