#!/usr/bin/env python
# Copyright 2012 Samsung SDS

import pycassa
import os
import sys

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "synaps", "__init__.py")):
    sys.path.insert(0, possible_topdir)

from synaps import flags
from synaps import log as logging
from synaps import utils

import storm
import json
from synaps_constants import PUT_METRIC_DATA_MSG_ID

class UnpackMessageBolt(storm.BasicBolt):
    def get_metric_id(self, message):
        return "metric_id"
    
    def process(self, tup):
        message_buf = tup.values[0]
        message = json.loads(message_buf)

        if message['msg_id'] == PUT_METRIC_DATA_MSG_ID:
            metric_id = self.get_metric_id(message)
            storm.emit([metric_id, message_buf])

UnpackMessageBolt().run()
