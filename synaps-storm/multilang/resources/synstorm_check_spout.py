#!/usr/bin/env python -u

# Copyright (c) 2012 Samsung SDS Co., LTD
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import sys
import traceback
import time
from synaps.db import Cassandra

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "synaps", "__init__.py")):
    sys.path.insert(0, possible_topdir)

from synaps import flags
from synaps import log as logging
from synaps import utils

from synaps.rpc import CHECK_METRIC_ALARM_MSG_ID
from storm import Spout, emit, log
from uuid import uuid4
import json

flags.FLAGS(sys.argv)
utils.default_flagfile()
logging.setup()
FLAGS = flags.FLAGS

class CheckSpout(Spout):
    SPOUT_NAME = "CheckSpout"
    lastchecked = 0
    
    def initialize(self, conf, context):
        self.pid = os.getpid()
        self.cass = Cassandra()
        self.nextTuple()
        self.delivery_tags = {}
        self.lastchecked = time.time()
    
    def log(self, msg):
        log("[%s:%d] %s" % (self.SPOUT_NAME, self.pid, msg))
        
    def tracelog(self, e):
        msg = traceback.format_exc(e)
        for line in msg.splitlines():
            self.log("TRACE: " + line)
    
    def nextTuple(self):
        now = time.time()
        if self.lastchecked == 0:
            self.lastchecked = now
        elif now - self.lastchecked >= 60: 
            self.lastchecked = now
            id = "periodic_%s" % str(uuid4())
            body = json.dumps({'message_id': CHECK_METRIC_ALARM_MSG_ID})
            message = "Periodic monitoring message sent [%s] %s"
            self.log(message % (id, body))
            emit([None, body], id=id)
        else:
            time.sleep(1)

if __name__ == "__main__":
    CheckSpout().run()
