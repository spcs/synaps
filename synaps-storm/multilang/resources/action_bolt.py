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

import md5
import json
import storm
import traceback
from synaps.db import Cassandra
from synaps.rpc import (PUT_METRIC_DATA_MSG_ID, PUT_METRIC_ALARM_MSG_ID,
                        DELETE_ALARMS_MSG_ID, SET_ALARM_STATE_MSG_ID)
from synaps.utils import validate_email, validate_international_phonenumber

threshhold = 10000
flags.FLAGS(sys.argv)
utils.default_flagfile()
logging.setup()

class ActionBolt(storm.BasicBolt):
    def initialize(self, stormconf, context):
        self.cass = Cassandra()
    
    def log(self, msg):
        storm.log("[ActionBolt] " + msg)

    def send_sms(self, action, message):
        self.log("%s %s" % (action, message))
    
    def send_email(self, action, message):
        self.log("%s %s" % (action, message))
    
    def do_action(self, action, message):
        def get_action_type(action):
            if validate_email(action):
                return "email"
            elif validate_international_phonenumber(action):
                return "SMS"
        
        action_type = get_action_type(action)
        if action_type == "email":
            self.send_email(action, message)
        elif action_type == "SMS":
            self.send_sms(action, message)
    
    def process(self, tup):
        alarm_key = tup.values[0]
        message_buf = tup.values[1]
        message = json.loads(message_buf)
        actions = []
        
        alarm = self.cass.get_metric_alarm(UUID(alarm_key))
        if alarm['actions_enabled']:
            if message['state'] == 'OK':
                actions = json.loads(alarm['ok_actions'])
            elif message['state'] == 'INSUFFICIENT_DATA':
                actions = json.loads(alarm['insufficient_data_actions'])
            elif message['state'] == 'ALARM':
                actions = json.loads(alarm['alarm_actions'])
            
            for action in actions:
                self.do_action(action, message)
        
        self.log("message received: %s " % message_buf)

ActionBolt().run()
