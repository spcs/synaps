#!/usr/bin/env python
# Copyright 2012 Samsung SDS

import os
import sys

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "synaps", "__init__.py")):
    sys.path.insert(0, possible_topdir)

from synaps import flags
from synaps import log as logging
from synaps import utils
from synaps.db import Cassandra

import storm
import json
from synaps_constants import PUT_METRIC_DATA_MSG_ID

class UnpackMessageBolt(storm.BasicBolt):
    def initialize(self, stormconf, context):
        self.cass = Cassandra()
    
    def get_metric_key(self, message):
        return self.cass.get_metric_key_or_create(message['project_id'],
                                                  message['namespace'],
                                                  message['metric_name'],
                                                  message['dimensions'])
    
    def process(self, tup):
        message_buf = tup.values[0]
        message = json.loads(message_buf)
        
        if message['message_id'] == PUT_METRIC_DATA_MSG_ID:
            metric_key = str(self.get_metric_key(message))
            storm.emit([metric_key, message_buf])

UnpackMessageBolt().run()
