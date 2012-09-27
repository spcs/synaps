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
possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "synaps", "__init__.py")):
    sys.path.insert(0, possible_topdir)

from synaps import flags
from synaps import log as logging
from synaps import utils
from uuid import UUID

import md5
import json
import storm
import traceback
from synaps.db import Cassandra
from synaps.rpc import (PUT_METRIC_DATA_MSG_ID, PUT_METRIC_ALARM_MSG_ID,
                        DELETE_ALARMS_MSG_ID, SET_ALARM_STATE_MSG_ID)

threshhold = 10000
flags.FLAGS(sys.argv)
utils.default_flagfile()
logging.setup()

class UnpackMessageBolt(storm.BasicBolt):
    BOLT_NAME = "UnpackMessageBolt"
    
    def initialize(self, stormconf, context):
        self.cass = Cassandra()
        self.key_dict = {}
    
    def log(self, msg):
        storm.log("[%s] %s" % (self.BOLT_NAME, msg))
        
    def tracelog(self, e):
        msg = traceback.format_exc(e)
        for line in msg.splitlines():
            self.log("TRACE: " + line)
                
    def get_metric_key(self, message):
        memory_key = md5.md5(str((message['project_id'],
                                  message['namespace'],
                                  message['metric_name'],
                                  message['dimensions']))).digest()
        
        if memory_key not in self.key_dict:
            if len(self.key_dict) > threshhold:
                self.key_dict.popitem()
            
            self.key_dict[memory_key] = self.cass.get_metric_key_or_create(
                 message['project_id'], message['namespace'],
                 message['metric_name'], message['dimensions'],
                 message['unit']
            )
            
        return self.key_dict[memory_key]
    
    def get_alarm_metric_key(self, alarmkey):
        alarm = self.cass.get_metric_alarm(alarmkey)
        if alarm:
            return str(alarm.get('metric_key'))
        else:
            return None
    
    def process(self, tup):
        message_buf = tup.values[0]
        message = json.loads(message_buf)

        try:
            message_id = message.get('message_id')
            if message_id == PUT_METRIC_DATA_MSG_ID:
                metric_key = str(self.get_metric_key(message))
                storm.emit([metric_key, message_buf])
            elif message_id == PUT_METRIC_ALARM_MSG_ID:
                metric_key = message.get('metric_key')
                storm.emit([metric_key, message_buf])
            elif message_id == DELETE_ALARMS_MSG_ID:
                project_id = message.get('project_id')
                alarmkeys = message.get('alarmkeys')
                for alarmkey in alarmkeys:
                    try:
                        alarmkey_uuid = UUID(alarmkey)
                        metric_key = self.get_alarm_metric_key(alarmkey_uuid)
                        metric_key = str(metric_key)
                        if metric_key:
                            message['alarmkey'] = alarmkey
                            storm.emit([metric_key, json.dumps(message)])
                    except Exception as e:
                        storm.log("Alarm %s does not exists" % alarmkey)
                        storm.log(traceback.format_exc(e))
            elif message_id == SET_ALARM_STATE_MSG_ID:
                project_id = message.get('project_id')
                alarm_name = message.get('alarm_name')
                alarm_key = self.cass.get_metric_alarm_key(project_id,
                                                           alarm_name)
                alarm = self.cass.get_metric_alarm(alarm_key)
                metric_key = str(alarm.get('metric_key'))
                storm.emit([metric_key, json.dumps(message)])
        except Exception as e:
            storm.log(traceback.format_exc(e))
            storm.fail(tup)

if __name__ == "__main__":
    UnpackMessageBolt().run()
