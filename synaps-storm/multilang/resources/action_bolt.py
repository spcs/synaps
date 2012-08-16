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
from uuid import UUID

import md5
import json
import storm
import traceback
from synaps.db import Cassandra
from synaps.rpc import (PUT_METRIC_DATA_MSG_ID, PUT_METRIC_ALARM_MSG_ID,
                        DELETE_ALARMS_MSG_ID, SET_ALARM_STATE_MSG_ID)

threshhold = 10000
flags.FLAGS(sys.argv)
utils.default_flagfile()
logging.setup()

class ActionBolt(storm.BasicBolt):
    def initialize(self, stormconf, context):
        self.cass = Cassandra()
    
    def process(self, tup):
        message_buf = tup.values[0]
        message = json.loads(message_buf)
        storm.log("[ActionBolt] received: %s " % message_buf)


ActionBolt().run()
