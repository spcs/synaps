#!/usr/bin/env python
# Copyright 2012 Samsung SDS

import os
import sys
import traceback
import pika

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "synaps", "__init__.py")):
    sys.path.insert(0, possible_topdir)

from synaps import flags
from synaps import utils

from storm import Spout, emit, log
from uuid import uuid4

FLAGS = flags.FLAGS

class ApiSpout(Spout):
    def initialize(self, conf, context):
        self.connect()
        self.delivery_tags = {}
    
    def connect(self):
        self.conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=FLAGS.get('rabbitmq_server'))
        )
        
        self.channel = self.conn.channel()
        queue_args = {"x-ha-policy" : "all" }
        self.channel.queue_declare(queue='metric_queue', durable=True,
                                   arguments=queue_args)
    
    def ack(self, id):
        if id in self.delivery_tags:
            tag, try_count = self.delivery_tags.pop(id)
            self.channel.basic_ack(delivery_tag=tag)
            log("[%s] message acked" % id)
    
    def fail(self, id):
        if id in self.delivery_tags:
            tag, try_count = self.delivery_tags.get(id)
            if try_count < 10:
                self.delivery_tags[id] = (tag, try_count + 1)
                log("retry failed message [%s]" % id)
            else:
                self.channel.basic_ack(delivery_tag=tag)
                log("discard failed message [%s]" % id)
    
    def nextTuple(self):
        try:
            (method_frame, header_frame, body) = self.channel.basic_get(
                queue="metric_queue"
            )
    
            if not method_frame.NAME == 'Basic.GetEmpty':
                id = str(uuid4())
                message = "Start processing message in the queue - [%s] %s"
                log(message % (id, body))
                self.delivery_tags[id] = (method_frame.delivery_tag, 0)
                emit([body], id=id)
                
        except Exception as e:
            log(traceback.format_exc(e))

if __name__ == "__main__":
    flags.FLAGS(sys.argv)
    utils.default_flagfile()
    ApiSpout().run()
