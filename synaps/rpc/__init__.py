# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 Red Hat, Inc.
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

from eventlet.pools import TokenPool
from synaps import flags
from synaps.utils import strtime
from synaps import log as logging
from synaps.exception import RpcInvokeException
import uuid, time
import pika, json

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS

PUT_METRIC_DATA_MSG_ID = 0x0001
PUT_METRIC_ALARM_MSG_ID = 0x0002
DISABLE_ALARM_ACTIONS = 0x0003
ENABLE_ALARM_ACTIONS = 0x0004
DELETE_ALARMS_MSG_ID = 0x0005
SET_ALARM_STATE_MSG_ID = 0x0006
CHECK_METRIC_ALARM_MSG_ID = 0x0010 


def retry5_uncaught_exceptions(infunc):
    def inner_func(*args, **kwargs):
        last_log_time = 0
        last_exc_message = None
        exc_count = 0
        for i in range(5):
            try:
                return infunc(*args, **kwargs)
            except Exception as exc:
                if exc.message == last_exc_message:
                    exc_count += 1
                else:
                    exc_count = 1
                # Do not log any more frequently than once a minute unless
                # the exception message changes
                cur_time = int(time.time())
                if (cur_time - last_log_time > 60 or
                        exc.message != last_exc_message):
                    LOG.exception(
                        _('Unexpected exception occurred %d time(s)... '
                          'retrying.') % exc_count)
                    last_log_time = cur_time
                    last_exc_message = exc.message
                    exc_count = 0
                # This should be a very rare event. In case it isn't, do
                # a sleep.
                time.sleep(1)
    return inner_func

class RemoteProcedureCall(object):
    def __init__(self):
        self.pool = TokenPool(create=self.open_channel, max_size=1000)

    def open_channel(self):
        host = FLAGS.get('rabbit_host')
        port = FLAGS.get('rabbit_port')
        LOG.info(_("connecting to rabbit_host %s %d") % (host, port))

        credentials=pika.PlainCredentials(FLAGS.get('rabbit_userid'),
                                          FLAGS.get('rabbit_password'))
        con_param = pika.ConnectionParameters(
                        host=FLAGS.get('rabbit_host'),
                        port=FLAGS.get('rabbit_port'), 
                        credentials=credentials,
                        virtual_host=FLAGS.get('rabbit_virtual_host'))
        conn = pika.BlockingConnection(con_param)
        
        channel = conn.channel()
        queue_args = {"x-ha-policy" : "all" }
        channel.queue_declare(queue='metric_queue', durable=True,
                              arguments=queue_args)
        channel.confirm_delivery()
        return channel

    
    @retry5_uncaught_exceptions
    def send_msg(self, message_id, body):
        """
        
        
        Args:
            message_id: int
                ex) PUT_METRIC_DATA_MSG_ID (0x0001)
                    PUT_METRIC_ALARM_MSG_ID (0x0002)
                    ...
            body: dict object (will be converted into json format)
            
        """
        if type(message_id) is not int:
            raise RpcInvokeException()
        

        message_uuid = str(uuid.uuid4()) 
        body.setdefault('message_id', message_id)
        body.setdefault('message_uuid', message_uuid)
        
        expiration = '60000' if message_id == PUT_METRIC_DATA_MSG_ID else None
        delivery_mode = 1 if message_id == PUT_METRIC_DATA_MSG_ID else 2
        properties=pika.BasicProperties(delivery_mode=delivery_mode, 
                                        expiration=expiration)
        
        with self.pool.item() as channel:
            if not channel.is_open:
                channel = self.open_channel()
            
            channel.basic_publish(exchange='', routing_key='metric_queue', 
                                  body=json.dumps(body), properties=properties)
            
        LOG.info(_("send_msg - id(%03d), %s"), message_id, message_uuid)
        LOG.debug(_("send_msg - body(%s)"), str(body))
            
