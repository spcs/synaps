# Copyright 2012 Samsung SDS
# All Rights Reserved

from synaps import flags
from synaps.utils import strtime
from synaps import log as logging
from synaps.exception import RpcInvokeException

import pika, json

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS

PUT_METRIC_DATA_MSG_ID = 0x0001

class RemoteProcedureCall(object):
    def __init__(self):
        self.connect()
    
    def connect(self):
        try:
            self.conn = pika.BlockingConnection(
                pika.ConnectionParameters(host=FLAGS.get('rabbitmq_server'))
            )
            
            self.channel = self.conn.channel()
            self.channel.queue_declare(queue='metric_queue', durable=True)
        except:
            raise RpcInvokeException()
        
    def put_metric_data(self, project_id, namespace, metric_name, dimensions,
                        value, unit=None, timestamp=None):
        
        if not self.conn.is_open:
            self.connect()
        
        timestamp = strtime(timestamp) if timestamp else None

        message = {'project_id': project_id, 'namespace':namespace,
                   'metric_name': metric_name, 'dimensions': dimensions,
                   'value':value, 'unit':unit, 'timestamp':timestamp,
                   'message_id': PUT_METRIC_DATA_MSG_ID}
        
        self.channel.basic_publish(
            exchange='', routing_key='metric_queue', body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
