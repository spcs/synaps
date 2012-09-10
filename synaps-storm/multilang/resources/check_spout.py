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

from storm import Spout, emit, log
from uuid import uuid4

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
            now = time.localtime()
            if now.tm_sec%20 == 0:
                self.log(now)
                id = str(uuid4())
                body='{"message_id": 16}'
                emit([id,body])
                time.sleep(10)
                

        except Exception as e:
            self.tracelog(e)

if __name__ == "__main__":
    flags.FLAGS(sys.argv)
    utils.default_flagfile()
    CheckSpout().run()
