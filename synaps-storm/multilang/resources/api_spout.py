#!/usr/bin/env python
# Copyright 2012 Samsung SDS

import os
import sys
import pika

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "synaps", "__init__.py")):
    sys.path.insert(0, possible_topdir)

from synaps import flags
from synaps import utils

from storm import Spout, emit, log
from time import sleep
from uuid import uuid4
import json

FLAGS = flags.FLAGS

class ApiSpout(Spout):
    def initialize(self, conf, context):
        self.connect()
    
    def connect(self):
        self.conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=FLAGS.get('rabbitmq_server'))
        )
        
        self.channel = self.conn.channel()
        queue_args = {"x-ha-policy" : "all" }
        self.channel.queue_declare(queue='metric_queue', durable=True,
                                   arguments=queue_args)   
    
    def nextTuple(self):
        try:
            (method_frame, header_frame, body) = self.channel.basic_get(
                queue="metric_queue"
            )
    
            if not method_frame.NAME == 'Basic.GetEmpty':
                log("rabbitmq - get %s" % body)
                self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                emit([body], id=str(uuid4()))
        except Exception as e:
            log(traceback.format_exc(e))

if __name__ == "__main__":
    flags.FLAGS(sys.argv)
    utils.default_flagfile()
    ApiSpout().run()
