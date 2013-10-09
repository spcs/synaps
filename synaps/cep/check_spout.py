# Copyright (c) 2012, 2013 Samsung SDS Co., LTD
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
import time
from uuid import uuid4

from synaps.cep.storm import Spout, emit
from synaps.db import Cassandra
from synaps import flags
from synaps import log as logging
from synaps.rpc import CHECK_METRIC_ALARM_MSG_ID


LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS


class CheckSpout(Spout):
    SPOUT_NAME = "CheckSpout"
    lastchecked = 0
    check_counter = 0
    warmup_period = 3
    
    def initialize(self, conf, context):
        self.pid = os.getpid()
        self.cass = Cassandra()
        self.nextTuple()
        self.delivery_tags = {}
        self.lastchecked = self.get_now()


    def ack(self, id):
        LOG.info("Acked message %s", id)
        
            
    def fail(self, id):
        LOG.error("Reject failed message %s", id)
        
        
    def get_now(self):
        return datetime.utcnow().replace(second=0, microsecond=0)

    
    def nextTuple(self):
        now = self.get_now()
        
        if self.lastchecked != now:
            self.check_counter += 1
            if self.check_counter <= self.warmup_period:
                LOG.info("warming up. skipping evaluation. counter: %d", 
                         self.check_counter)
                return
            self.lastchecked = now
            id = "periodic_%s" % str(uuid4())
            body = json.dumps({'message_id': CHECK_METRIC_ALARM_MSG_ID})
            LOG.info("Periodic monitoring message sent [%s] %s. counter: %d", 
                     id, body, self.check_counter)
            emit([None, body], id=id)
        else:
            time.sleep(1)
