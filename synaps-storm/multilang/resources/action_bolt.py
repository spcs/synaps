#!/usr/bin/env python
# Copyright 2012 Samsung SDS

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

import json
import storm
import traceback
import zmq
from synaps.db import Cassandra
from synaps.utils import validate_email, validate_international_phonenumber

threshhold = 10000
FLAGS = flags.FLAGS

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
    
    def process(self, tup):
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

if __name__ == "__main__":
    flags.FLAGS(sys.argv)
    utils.default_flagfile()
    logging.setup()
    ActionBolt().run()
