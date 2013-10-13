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
from uuid import UUID

from synaps import flags
from synaps.cep import storm
from synaps.db import Cassandra
from synaps import log as logging
from synaps import utils
from synaps.rpc import (PUT_METRIC_DATA_MSG_ID, PUT_METRIC_ALARM_MSG_ID,
                        DELETE_ALARMS_MSG_ID, SET_ALARM_STATE_MSG_ID)

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS

if FLAGS.memcached_servers:
    import memcache
else:
    from synaps.common import memorycache as memcache
    

class UnpackMessageBolt(storm.BasicBolt):
    BOLT_NAME = "UnpackMessageBolt"
    
    def initialize(self, stormconf, context):
        self.pid = os.getpid()
        self.cass = Cassandra()
        self.key_dict = {}
        self.mc = memcache.Client(FLAGS.memcached_servers, debug=0)
    
                
    def get_metric_key(self, message):
        project_id = message['project_id']
        namespace = message['namespace']
        metric_name = message['metric_name']
        dimensions = message['dimensions']
        unit = message['unit']
        
        key = utils.generate_metric_key(project_id, namespace, metric_name, 
                                        dimensions)
        memory_key = "metric_%s" % str(key)
        metric_key = self.mc.get(memory_key)
        
        if not metric_key:
            metric_key = self.cass.get_metric_key_or_create(project_id, 
                                    namespace, metric_name, dimensions, unit)
            self.mc.set(memory_key, metric_key, 3000)

        return metric_key
    
    
    def get_alarm_metric_key(self, alarmkey):
        alarm = self.cass.get_metric_alarm(alarmkey)
        if alarm:
            return str(alarm.get('metric_key'))
        else:
            return None

    
    def process(self, tup):
        message_buf = tup.values[0]
        message = json.loads(message_buf)

        message_id = message['message_id']
        message_uuid = message['message_uuid']
        LOG.info("start processing msg[%s:%s]" % (message_id, message_uuid))
        
        if message_id == PUT_METRIC_DATA_MSG_ID:
            metric_key = str(self.get_metric_key(message))
            storm.emit([metric_key, message_buf])
        
        elif message_id == PUT_METRIC_ALARM_MSG_ID:
            metric_key = message.get('metric_key')
            storm.emit([metric_key, message_buf])

        elif message_id == DELETE_ALARMS_MSG_ID:
            project_id = message['project_id']
            alarmkeys = message['alarmkeys']
            for alarmkey in alarmkeys:
                try:
                    alarmkey_uuid = UUID(alarmkey)
                    metric_key = self.get_alarm_metric_key(alarmkey_uuid)
                    metric_key = str(metric_key)
                    if metric_key:
                        message['alarmkey'] = alarmkey
                        storm.emit([metric_key, json.dumps(message)])
                except Exception as e:
                    LOG.error("Alarm %s does not exists", alarmkey)

        elif message_id == SET_ALARM_STATE_MSG_ID:
            project_id = message['project_id']
            alarm_name = message['alarm_name']
            alarm_key = self.cass.get_metric_alarm_key(project_id,
                                                       alarm_name)
            if alarm_key:
                alarm = self.cass.get_metric_alarm(alarm_key)
                metric_key = str(alarm['metric_key'])
                storm.emit([metric_key, json.dumps(message)])
