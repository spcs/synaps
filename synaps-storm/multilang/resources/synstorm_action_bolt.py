#!/usr/bin/env python -u
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
# from synaps import log as logging
from synaps import utils
from uuid import UUID, uuid4

import smtplib
import MySQLdb as db
from email.mime.text import MIMEText
from random import randint

import json
import storm
import traceback
from synaps.db import Cassandra
from synaps.utils import validate_email, validate_international_phonenumber

flags.FLAGS(sys.argv)
utils.default_flagfile()
# logging.setup()
FLAGS = flags.FLAGS

SMTP_SERVER = FLAGS.get('smtp_server')
MAIL_SENDER = FLAGS.get('mail_sender')
SMS_SENDER = FLAGS.get('sms_sender')
SMS_DB_HOST = FLAGS.get('sms_database_host')
SMS_DB_PORT = FLAGS.get('sms_database_port')
SMS_DB = FLAGS.get('sms_database')
SMS_DB_USERNAME = FLAGS.get('sms_db_username')
SMS_DB_PASSWORD = FLAGS.get('sms_db_password')


class ActionBolt(storm.BasicBolt):
    BOLT_NAME = "ActionBolt"
    ENABLE_SEND_MAIL = FLAGS.get('enable_send_mail')
    ENABLE_SEND_SMS = FLAGS.get('enable_send_sms')
    NOTIFICATION_SERVER = FLAGS.get('notification_server_addr')
    STATISTICS_TTL = FLAGS.get('statistics_ttl')
    
    def initialize(self, stormconf, context):
        self.pid = os.getpid()
        self.cass = Cassandra()
    
    def log(self, msg):
        storm.log("[%s:%d] %s" % (self.BOLT_NAME, self.pid, msg))
        
    def tracelog(self, e):
        msg = traceback.format_exc(e)
        for line in msg.splitlines():
            self.log("TRACE: " + line)
    
    def get_action_type(self, action):
        if validate_email(action):
            return "email"
        elif validate_international_phonenumber(action):
            return "SMS"

    
    def alarm_history_state_update(self, alarmkey, alarm,
                                   notification_message):
        """
        update alarm history based on notification message
        
        notification_message = {
            'method': "email",
            'receivers': email_receivers,
            'subject': message['subject'],
            'body': message['body'],
            'state': "ok" | "failed"
        }
        """        
        item_type = 'Action'
        project_id = alarm['project_id']
        if notification_message.get('state', 'ok') == 'ok':
            history_summary = "Message '%(subject)s' is sent via"\
                              " %(method)s" % notification_message
        else:
            history_summary = "Failed to send a message '%(subject)s' via"\
                              " %(method)s" % notification_message
        
        timestamp = utils.utcnow()
        
        history_key = uuid4()
        column = {'project_id':project_id,
                  'alarm_key':UUID(alarmkey),
                  'alarm_name':alarm['alarm_name'],
                  'history_data': json.dumps(notification_message),
                  'history_item_type':item_type,
                  'history_summary':history_summary,
                  'timestamp':timestamp}
        
        self.cass.insert_alarm_history(history_key, column, 
                                       ttl=self.STATISTICS_TTL)
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
        self.log("start processing tup %s" % (tup))
        
        alarm = self.cass.get_metric_alarm(UUID(alarm_key))
        
        try:
            actions_enabled = alarm['actions_enabled']
        except TypeError:
            msg = "alarm is not found [" + alarm_key + "]"
            self.log(msg)
            
            return False
                     
        if message['state'] == 'OK':
            actions = json.loads(alarm['ok_actions'])
        elif message['state'] == 'INSUFFICIENT_DATA':
            actions = json.loads(alarm['insufficient_data_actions'])
        elif message['state'] == 'ALARM':
            actions = json.loads(alarm['alarm_actions'])
        
        self.log("actions enabled: %s actions: %s " % (actions_enabled,
                                                       actions))
        if actions_enabled and actions:                 
            if self.ENABLE_SEND_SMS:
                sms_receivers = [action for action in actions
                                 if self.get_action_type(action) == "SMS"]
                 
                notification_message = {
                    'method': "SMS",
                    'receivers': sms_receivers,
                    'subject': message['subject'],
                    'body': message['body'],
                    'state': 'ok'
                }
                
                if sms_receivers: 
                    try:
                        self.send_sms(notification_message)
                    except Exception as e:
                        notification_message['state'] = 'failed'
                        self.tracelog(e)
                    self.log("AUDIT notify: %s" % notification_message)
                    self.alarm_history_state_update(alarm_key, alarm,
                                                    notification_message)

            if self.ENABLE_SEND_MAIL:            
                email_receivers = [action for action in actions 
                                   if self.get_action_type(action) == "email"]
                 
                notification_message = {
                    'method': "email",
                    'receivers': email_receivers,
                    'subject': message['subject'],
                    'body': message['body'],
                    'state': 'ok'
                }
                
                if email_receivers:
                    try:                
                        self.send_email(notification_message)
                    except Exception as e:
                        notification_message['state'] = 'failed'
                        self.tracelog(e)
                    self.log("AUDIT notify: %s" % notification_message)
                    self.alarm_history_state_update(alarm_key, alarm,
                                                    notification_message)
                    

    def send_sms(self, message):
        Q_LOCAL = """insert into SMS_SEND(REG_TIME, MSG_KEY, RECEIVER, SENDER, 
        MESSAGE) values (now()+0, '%d','%s','%s','%s')
        """
        Q_NAT = """insert into SMS_SEND(REG_TIME, MSG_KEY, RECEIVER, SENDER, 
        MESSAGE, NAT_CODE) values (now()+0, '%d','%s','%s','%s', %d)
        """
    
        def build_query(receiver, subject):
            nat, local_no = parse_number(receiver)
            # random integer for msg_key
            msg_key = randint(1, 10 ** 15)
            if len(subject) > 80:
                subject = subject[:77] + "..."
            
            if nat == None:
                ret = Q_LOCAL % (msg_key, local_no, SMS_SENDER, subject)
            else:
                ret = Q_NAT % (msg_key, local_no, SMS_SENDER, subject, nat)
            return ret
            
        def parse_number(no):
            nat, local_no = no.split(' ', 1)
            if nat.startswith("+"):
                nat = int(nat[1:])
            else:
                nat = int(nat)
            
            if nat == 82:  # Korean national code
                nat = None
                local_no = '0' + local_no.replace(' ', '')
            else:
                local_no = local_no.replace(' ', '')
            
            return nat, local_no
        
        self.log("SMS: %s" % str(message))
        
        # message example.
        #
        #    {'body': u'Threshold Crossed: 3 datapoints were greater than the threshold(50.000000). The most recent datapoints: [110.0, 110.0, 60.0]. at 2012-08-28T10:17:50.494902',
        #     'receivers': [u'+82 1093145616'],
        #     'method': 'SMS',
        #     'subject': u'AlarmActionTest state has been changed from OK to ALARM at 2012-08-28T10:17:50.494902'}
        #
    
        self.log("connect to mysql db %s@%s:%s %s" % (SMS_DB_USERNAME,
                 SMS_DB_HOST, SMS_DB_PORT, SMS_DB))
        conn = db.connect(host=SMS_DB_HOST, port=SMS_DB_PORT, db=SMS_DB,
                          user=SMS_DB_USERNAME, passwd=SMS_DB_PASSWORD,
                          connect_timeout=30)
        c = conn.cursor()
        for receiver in message['receivers']:
            q = build_query(receiver, message['subject'])
            c.execute(q)
        
        c.close()
        conn.commit()
        conn.close()
        
    
    def send_email(self, message):
        self.log("EMAIL: %s" % str(message))
    
        msg = MIMEText(message['body'])
        msg['Subject'] = message['subject']
        msg['From'] = MAIL_SENDER
        msg['To'] = ", ".join(message['receivers'])
        
        s = smtplib.SMTP(SMTP_SERVER, timeout=30)
        s.sendmail(MAIL_SENDER, message['receivers'], msg.as_string())
        s.quit()
    
    
    def process(self, tup):
        self.process_action(tup)
        

if __name__ == "__main__":
    ActionBolt().run()
