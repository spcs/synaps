#!/usr/bin/env python
# Copyright 2012 Samsung SDS

'''
Created on Aug 29, 2012

@author: Roh Jeong won
'''
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
from synaps import utils
from synaps.rpc import CHECK_METRIC_ALARM_MSG_ID
from storm import Spout, emit, log
from uuid import uuid4
import json

FLAGS = flags.FLAGS

class CheckSpout(Spout):
    SPOUT_NAME = "CheckSpout"
    
    def initialize(self, conf, context):
        self.cass = Cassandra()
        self.nextTuple()
        self.delivery_tags = {}
    
    def log(self, msg):
        log("[%s] %s" % (self.SPOUT_NAME, msg))
        
    def tracelog(self, e):
        msg = traceback.format_exc(e)
        for line in msg.splitlines():
            self.log("TRACE: " + line)
    
    def nextTuple(self):
        try:
            id = "periodic_%s" % str(uuid4())
            body = json.dumps({'message_id': CHECK_METRIC_ALARM_MSG_ID})
            emit([None, body], id=id)
            time.sleep(60)
                
        except Exception as e:
            self.tracelog(e)

if __name__ == "__main__":
    flags.FLAGS(sys.argv)
    utils.default_flagfile()
    CheckSpout().run()
