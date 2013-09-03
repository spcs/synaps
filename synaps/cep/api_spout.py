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

import json
import os
import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError
import time

from synaps.cep.storm import Spout, emit
from synaps import flags
from synaps import log as logging


LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS


class ApiSpout(Spout):
    SPOUT_NAME = "APISpout"
    
    def initialize(self, conf, context):
        self.pid = os.getpid()       
        self.connect()
    
    def connect(self):
        while True:
            try:
                self._connect()
            except (AMQPConnectionError, AMQPChannelError):
                LOG.warn("AMQP Connection Error. Retry in 3 seconds.")
                time.sleep(3)            
            else:
                break
    
    def _connect(self):
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
        LOG.info("Acked message %s", id)
        
            
    def fail(self, id):
        LOG.error("Reject failed message %s", id)
        
    
    def nextTuple(self):
        try:
            (method_frame, header_frame, body) = self.channel.basic_get(
                queue="metric_queue", no_ack=True
            )
        except (AMQPConnectionError, AMQPChannelError):
            LOG.error("AMQP Connection or Channel Error. While get a message.")
            self.connect()
            return

        if method_frame:
            mq_msg_id = method_frame.delivery_tag
            msg_body = json.loads(body)
            msg_id, msg_uuid = msg_body['message_id'], msg_body['message_uuid']
            message = "Start processing message in the queue - [%s:%s] %s"
            LOG.info(message % (msg_id, msg_uuid, body))
            emit([body], id=msg_uuid)
