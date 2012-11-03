#!/usr/bin/env python
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
import pika
import json
import uuid
import time
from pika.exceptions import AMQPConnectionError

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "synaps", "__init__.py")):
    sys.path.insert(0, possible_topdir)

from synaps import flags
from synaps import utils

from storm import Spout, emit, log
from uuid import uuid4

FLAGS = flags.FLAGS
flags.FLAGS(sys.argv)
utils.default_flagfile()

class ApiSpout(Spout):
    SPOUT_NAME = "APISpout"
    
    def initialize(self, conf, context):
        self.connect()
        self.delivery_tags = {}
    
    def log(self, msg):
        log("[%s] %s" % (self.SPOUT_NAME, msg))
        
    def tracelog(self, e):
        msg = traceback.format_exc(e)
        for line in msg.splitlines():
            self.log("TRACE: " + line)
    
    def connect(self):
        self.conn = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=FLAGS.get('rabbit_host'),
                port=FLAGS.get('rabbit_port'),
                credentials=pika.PlainCredentials(
                    FLAGS.get('rabbit_userid'),
                    FLAGS.get('rabbit_password')
                ),
                virtual_host=FLAGS.get('rabbit_virtual_host'),
            )
        )        
        
        self.channel = self.conn.channel()
        queue_args = {"x-ha-policy" : "all" }
        self.channel.queue_declare(queue='metric_queue', durable=True,
                                   arguments=queue_args)
    
    def ack(self, id):
        if id in self.delivery_tags:
            tag, try_count = self.delivery_tags.pop(id)
            self.channel.basic_ack(delivery_tag=tag)
            self.log("[%s] message acked" % id)
    
    def fail(self, id):
        if id in self.delivery_tags:
            tag, try_count = self.delivery_tags.get(id)
            if try_count < 10:
                self.delivery_tags[id] = (tag, try_count + 1)
                self.log("retry failed message [%s]" % id)
            else:
                self.channel.basic_ack(delivery_tag=tag)
                self.delivery_tags.pop(id)
                self.log("discard failed message [%s]" % id)
    
    def nextTuple(self):
        try:
            (method_frame, header_frame, body) = self.channel.basic_get(
                queue="metric_queue",
            )
        except AMQPConnectionError:
            msg = "AMQP Connection Error. Retry in 3 seconds."
            self.log(_(msg))
            time.sleep(3)            
            self.connect()
            self.delivery_tags = {}
            return

        if not method_frame.NAME == 'Basic.GetEmpty':
            try:
                unpacked_message = json.loads(body)
                id = unpacked_message.get('message_uuid', str(uuid.uuid4()))
                message = "Start processing message in the queue - [%s] %s"
                self.log(message % (id, body))
                self.delivery_tags[id] = (method_frame.delivery_tag, 0)
                emit([body], id=id)
            except Exception as e:
                self.tracelog(e)
                self.fail(id)

if __name__ == "__main__":
    ApiSpout().run()
