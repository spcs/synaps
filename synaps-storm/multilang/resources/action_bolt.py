#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

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
from uuid import UUID, uuid4

import json
import storm
import traceback
import zmq
from synaps.db import Cassandra
from synaps.utils import validate_email, validate_international_phonenumber

threshhold = 10000
FLAGS = flags.FLAGS

flags.FLAGS(sys.argv)
utils.default_flagfile()
logging.setup()

class ActionBolt(storm.BasicBolt):
    BOLT_NAME = "ActionBolt"
    ENABLE_SEND_MAIL = FLAGS.get('enable_send_mail')
    ENABLE_SEND_SMS = FLAGS.get('enable_send_sms')
    NOTIFICATION_SERVER = FLAGS.get('notification_server_addr')
    
    def initialize(self, stormconf, context):
        self.cass = Cassandra()
        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.PUSH)
        self.sock.connect(self.NOTIFICATION_SERVER)
    
    def log(self, msg):
        storm.log("[%s] %s" % (self.BOLT_NAME, msg))
        
    def tracelog(self, e):
        msg = traceback.format_exc(e)
        for line in msg.splitlines():
            self.log("TRACE: " + line)
    
    def get_action_type(self, action):
        if validate_email(action):
            return "email"
        elif validate_international_phonenumber(action):
            return "SMS"
        
    def do_action(self, action, message):
        
        action_type = self.get_action_type(action)
        if action_type == "email":
            self.send_email(action, message)
        elif action_type == "SMS":
            self.send_sms(action, message)
    
    def alarm_history_state_update(self, alarmkey, alarm, notification_message):
#                notification_message = {
#                    'method': "email",
#                    'receivers': email_receivers,
#                    'subject': message['subject'],
#                    'body': message['body']
#                }        
        item_type = 'Action'
        project_id = alarm['project_id']
        history_summary = ("Message '%(subject)s' is sent via %(method)s" % 
                           notification_message)
        timestamp = utils.utcnow()
        
        history_key = uuid4()
        column = {'project_id':project_id,
                  'alarm_key':UUID(alarmkey),
                  'alarm_name':alarm['alarm_name'],
                  'history_data': json.dumps(notification_message),
                  'history_item_type':item_type,
                  'history_summary':history_summary,
                  'timestamp':timestamp}
        
        self.cass.insert_alarm_history(history_key, column)
        storm.log("alarm history \n %s" % history_summary)
    
    def process_action(self, tup):
        """
        message example
        
        msg = {
            'state': new_state['stateValue'],
            'subject': "%s state has been changed from %s to %s" % 
                (alarm['alarm_name'], old_state['stateValue'],
                 new_state['stateValue']),
            'body': new_state['stateReason']
        }
        """        
        alarm_key = tup.values[0]
        message_buf = tup.values[1]
        message = json.loads(message_buf)
        self.log("message received: %s " % message_buf)
        
        alarm = self.cass.get_metric_alarm(UUID(alarm_key))
        actions_enabled = alarm['actions_enabled']
        if message['state'] == 'OK':
            actions = json.loads(alarm['ok_actions'])
        elif message['state'] == 'INSUFFICIENT_DATA':
            actions = json.loads(alarm['insufficient_data_actions'])
        elif message['state'] == 'ALARM':
            actions = json.loads(alarm['alarm_actions'])
        
        self.log("actions enabled: %s actions: %s " % (actions_enabled,
                                                       actions))
        if actions_enabled and actions:
            if self.ENABLE_SEND_MAIL:            
                email_receivers = [action for action in actions 
                                   if self.get_action_type(action) == "email"]
                
                notification_message = {
                    'method': "email",
                    'receivers': email_receivers,
                    'subject': message['subject'],
                    'body': message['body']
                }
                
                self.sock.send_pyobj(notification_message)
                self.log("notify: %s " % notification_message)
                self.alarm_history_state_update(alarm_key, alarm,
                                                notification_message)
                
            if self.ENABLE_SEND_SMS:
                sms_receivers = [action for action in actions
                                 if self.get_action_type(action) == "SMS"]
                
                notification_message = {
                    'method': "SMS",
                    'receivers': sms_receivers,
                    'subject': message['subject'],
                    'body': message['body']
                }
                
                self.sock.send_pyobj(notification_message)
                self.log("notify: %s " % notification_message)
                self.alarm_history_state_update(alarm_key, alarm,
                                                notification_message)    
    def process(self, tup):
        try:
            self.process_action(tup)
        except Exception as e:
            self.tracelog(e)
            storm.fail(tup)

if __name__ == "__main__":
    ActionBolt().run()
