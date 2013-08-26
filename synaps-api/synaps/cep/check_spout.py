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

from datetime import datetime
import json
import os
import traceback
import time
from uuid import uuid4

from synaps.cep.storm import Spout, emit, log
from synaps.db import Cassandra
from synaps import flags
from synaps import log as logging
from synaps.rpc import CHECK_METRIC_ALARM_MSG_ID


LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS


class CheckSpout(Spout):
    SPOUT_NAME = "CheckSpout"
    lastchecked = 0
    
    def initialize(self, conf, context):
        self.pid = os.getpid()
        self.cass = Cassandra()
        self.nextTuple()
        self.delivery_tags = {}
        self.lastchecked = self.get_now()
    
    def log(self, msg):
        LOG.info("[%s:%d] %s" % (self.SPOUT_NAME, self.pid, msg))
        
    def tracelog(self, e):
        msg = traceback.format_exc(e)
        for line in msg.splitlines():
            self.log("TRACE: " + line)

    def get_now(self):
        return datetime.utcnow().replace(second=0, microsecond=0)
    
    def nextTuple(self):
        now = self.get_now()
        
        if self.lastchecked != now:
            self.lastchecked = now
            id = "periodic_%s" % str(uuid4())
            body = json.dumps({'message_id': CHECK_METRIC_ALARM_MSG_ID})
            message = "Periodic monitoring message sent [%s] %s"
            self.log(message % (id, body))
            emit([None, body], id=id)
        else:
            time.sleep(1)
