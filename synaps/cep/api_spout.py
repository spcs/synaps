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

import eventlet
import json
import os
from synaps.cep.storm import Spout, emit
from synaps import flags
from synaps import log as logging
from synaps import rpc


LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS


class ApiSpout(Spout):
    SPOUT_NAME = "APISpout"
    
    def initialize(self, conf, context):
        LOG.info("API Spout is started")
        self.MAX_WORKERS = FLAGS.get('rabbit_read_workers')
        self.pid = os.getpid()
        self.worker_pool = eventlet.GreenPool(self.MAX_WORKERS)
        self.rpc = rpc.RemoteProcedureCall()
        self.queue = eventlet.Queue()
        
        
    def read_from_queue(self):
        while True:
            frame, body = self.rpc.read_msg()
            if frame:
                self.queue.put((frame, body))
                break
            else:
                eventlet.sleep(0.1)
                                              

    def ack(self, id):
        LOG.info("Acked message %s", id)
        
            
    def fail(self, id):
        LOG.error("Reject failed message %s", id)
        
    
    def nextTuple(self):
        if not self.worker_pool.waiting():
            self.worker_pool.spawn_n(self.read_from_queue)
        
        count = 0
        while (not self.queue.empty() and count < self.MAX_WORKERS):
            count += 1
            frame, body = self.queue.get()
            msg_body = json.loads(body)
            msg_id = msg_body['message_id']
            msg_req_id = ":".join((msg_body['message_uuid'], 
                                   msg_body['context']['request_id'],
                                   str(frame.delivery_tag)))
            message = "Start processing message in the queue - [%s:%s] %s"
            LOG.info(message, msg_id, msg_req_id, body)
            emit([body], id=msg_req_id)        
