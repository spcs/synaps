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

from email.mime.text import MIMEText
import os
import json
import MySQLdb as db
from random import randint
import smtplib
from uuid import UUID, uuid4

from synaps.cep import storm
from synaps.db import Cassandra
from synaps import flags
from synaps import log as logging
from synaps import utils
from synaps.utils import (validate_email, validate_international_phonenumber,
                          validate_instance_action, parse_instance_action, 
                          validate_groupnotification_action, 
                          parse_groupnotification_action)
from synaps.monitor import API
from synaps.context import get_admin_context

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS    


class ActionBolt(storm.BasicBolt):
    BOLT_NAME = "ActionBolt"
    
    def initialize(self, stormconf, context):
        self.pid = os.getpid()
        self.cass = Cassandra()
        self.enable_send_mail = FLAGS.get('enable_send_mail')
        self.enable_send_sms = FLAGS.get('enable_send_sms')
        self.enable_instance_action = FLAGS.get('enable_instance_action')
        self.notification_server = FLAGS.get('notification_server_addr')
        self.statistics_ttl = FLAGS.get('statistics_ttl')
        self.smtp_server = FLAGS.get('smtp_server')
        self.mail_sender = FLAGS.get('mail_sender')
        self.sms_sender = FLAGS.get('sms_sender')
        self.sms_db_host = FLAGS.get('sms_database_host')
        self.sms_db_port = FLAGS.get('sms_database_port')
        self.sms_db = FLAGS.get('sms_database')
        self.sms_db_username = FLAGS.get('sms_db_username')
        self.sms_db_password = FLAGS.get('sms_db_password')
        
        self.nova_auth_url = FLAGS.get('nova_auth_url')
        self.nova_admin_tenant_name = FLAGS.get('admin_tenant_name')
        self.nova_admin_user = FLAGS.get('admin_user')
        self.nova_admin_password = FLAGS.get('admin_password')
        
        self.api = API()
    
    
    def get_action_type(self, action):
        if validate_email(action):
            return "email"
        elif validate_international_phonenumber(action):
            return "SMS"
        elif validate_instance_action(action):
            return "InstanceAction"
        elif validate_groupnotification_action(action):
            return "GroupNotificationAction"


    def meter_sms_actions(self, project_id, receivers):
        ctxt = get_admin_context()
        local_receivers = [r for r in receivers if r.startswith("+82")]
        international_receivers = [r for r in receivers if not 
                                   r.startswith("+82")]
        
        self.api.put_metric_data(ctxt, project_id, namespace="SPCS/SYNAPS", 
                                 metric_name="LocalSMSActionCount", 
                                 dimensions={}, value=len(local_receivers), 
                                 unit="Count", 
                                 timestamp=utils.strtime(utils.utcnow()),
                                 is_admin=True)

        self.api.put_metric_data(ctxt, project_id, namespace="SPCS/SYNAPS", 
                                 metric_name="InternationalSMSActionCount", 
                                 dimensions={}, 
                                 value=len(international_receivers), 
                                 unit="Count", 
                                 timestamp=utils.strtime(utils.utcnow()),
                                 is_admin=True)
        
        LOG.audit("Meter SMS: %s %s %s", project_id, len(receivers), receivers)
        

    def meter_email_actions(self, project_id, receivers):
        ctxt = get_admin_context()
        self.api.put_metric_data(ctxt, project_id, namespace="SPCS/SYNAPS", 
                                 metric_name="EmailActionCount",
                                 dimensions={}, value=len(receivers), 
                                 unit="Count",
                                 timestamp=utils.strtime(utils.utcnow()), 
                                 is_admin=True)
        LOG.audit("Meter Email: %s %s %s", project_id, len(receivers), 
                  receivers)
        

    def meter_instance_actions(self, project_id, receivers):
        ctxt = get_admin_context()
        self.api.put_metric_data(ctxt, project_id, namespace="SPCS/SYNAPS", 
                                 metric_name="InstanceActionCount",
                                 dimensions={}, value=len(receivers), 
                                 unit="Count",
                                 timestamp=utils.strtime(utils.utcnow()), 
                                 is_admin=True)
        LOG.audit("Meter InstanceAction: %s %s %s", project_id, len(receivers), 
                  receivers)

    
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
        if notification_message.get("method") in ("email", "SMS"):
            if notification_message.get('state', 'ok') == 'ok':
                history_summary = "Message '%(subject)s' is sent via"\
                                  " %(method)s" % notification_message
            else:
                history_summary = "Failed to send a message '%(subject)s' via"\
                                  " %(method)s" % notification_message
        elif notification_message.get("method") in ("InstanceAction"):
            if notification_message.get('state', 'ok') == 'ok':
                history_summary = "%(method)s %(receivers)s is invoked." % \
                                  notification_message
            else:
                history_summary = "Failed to invoke %(method)s %(receivers)s."\
                                  % notification_message 
            
        
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
                                       ttl=self.statistics_ttl)
        LOG.info("History updated. %s", history_summary)
        
    
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
        def convert_group_notification(actions):
            ret = []
            for ac in actions:
                if validate_groupnotification_action(ac):
                    groupname = parse_groupnotification_action(ac)
                    new_actions = self.cass.get_notification_group(groupname)
                    ret += list(new_actions)
                else:
                    ret.append(ac)
            return ret
            
        alarm_key = tup.values[0]
        message_buf = tup.values[1]
        message = json.loads(message_buf)
        LOG.info("start processing tup %s", tup)
        
        alarm = self.cass.get_metric_alarm(UUID(alarm_key))
        
        try:
            actions_enabled = alarm['actions_enabled']
        except TypeError:
            LOG.debug("Alarm(%s) is not found", alarm_key)
            
            return False
                     
        if message['state'] == 'OK':
            actions = json.loads(alarm['ok_actions'])
        elif message['state'] == 'INSUFFICIENT_DATA':
            actions = json.loads(alarm['insufficient_data_actions'])
        elif message['state'] == 'ALARM':
            actions = json.loads(alarm['alarm_actions'])
            
        actions = convert_group_notification(actions)
        
        if actions_enabled and actions:                 
            if self.enable_send_sms:
                self.process_sms_action(alarm_key, alarm, message, actions)
            if self.enable_send_mail:
                self.process_email_action(alarm_key, alarm, message, actions)
            if self.enable_instance_action:
                self.process_instance_action(alarm_key, alarm, message, 
                                             actions)


    def do_instance_action(self, alarm_key, alarm, instance_actions):
        nc = utils.get_python_novaclient()
        
        for action in instance_actions:
            action_type, vm_uuid = parse_instance_action(action)
            server = nc.servers.get(vm_uuid)
            
            if action_type == "Migrate":
                server.migrate()
                LOG.info("instance action %s invoked for %s", action_type, 
                         server)
            elif action_type == "Reboot":
                server.reboot('HARD')
                LOG.info("instance action %s invoked for %s", action_type, 
                         server)
    

    def process_instance_action(self, alarm_key, alarm, message, actions):
        instance_actions = [action for action in actions 
                            if self.get_action_type(action) == 
                            "InstanceAction"]

        instance_action_message = {'method': "InstanceAction", 
                                   'receivers': instance_actions, 
                                   'subject': message['subject'],
                                   'body': message['body'], 'state': 'ok'}

        if instance_actions:
            try:
                self.do_instance_action(alarm_key, alarm, instance_actions)
            except Exception as e:
                instance_action_message['state'] = 'failed'
                LOG.exception(e)
            LOG.audit("InstanceAction is invoked. %s", instance_action_message)
            self.alarm_history_state_update(alarm_key, alarm,
                                            instance_action_message)
            if instance_action_message['state'] != 'failed':
                self.meter_instance_actions(alarm['project_id'], 
                                            instance_actions)
                

    def process_email_action(self, alarm_key, alarm, message, actions):
        email_receivers = list(set([action for action in actions 
                               if self.get_action_type(action) == "email"]))
         
        notification_message = {'method': "email", 
                                'receivers': email_receivers, 
                                'subject': message['subject'],
                                'body': message['body'], 'state': 'ok'}
        
        if email_receivers:
            try:                
                self.send_email(notification_message)
            except Exception as e:
                notification_message['state'] = 'failed'
                LOG.exception(e)
            LOG.audit("Email sent. %s", notification_message)
            self.alarm_history_state_update(alarm_key, alarm,
                                            notification_message)
            if notification_message['state'] != 'failed':
                self.meter_email_actions(alarm['project_id'], 
                                         email_receivers)
        
                    
    def process_sms_action(self, alarm_key, alarm, message, actions):
        sms_receivers = list(set([action for action in actions
                             if self.get_action_type(action) == "SMS"]))
         
        notification_message = {'method': "SMS", 'receivers': sms_receivers,
                                'subject': message['subject'], 
                                'body': message['body'], 'state': 'ok'}
        
        if sms_receivers: 
            try:
                self.send_sms(notification_message)
            except Exception as e:
                notification_message['state'] = 'failed'
                LOG.exception(e)
            LOG.audit("SMS sent. %s", notification_message)
            self.alarm_history_state_update(alarm_key, alarm,
                                            notification_message)
            if notification_message['state'] != 'failed':
                self.meter_sms_actions(alarm['project_id'], 
                                       sms_receivers)

    def send_sms(self, message):
        Q_LOCAL = """insert into MMS_SEND(REG_TIME, MSG_SEQ, MSG_KEY, 
        RECEIVER, SENDER, SUBJECT, MESSAGE) 
        values (now()+0, '%d', '%d', '%s', '%s', '%s', '%s')
        """
        
        Q_NAT = """insert into SMS_SEND(REG_TIME, MSG_KEY, RECEIVER, SENDER, 
        MESSAGE, NAT_CODE) values (now()+0, '%d','%s','%s','%s', %d)
        """
    
        def build_query(receiver, message):
            nat, local_no = parse_number(receiver)
            subject = message['subject']
            body = message['body']
            # random integer for msg_key
            msg_key = randint(1, 10 ** 15)
            
            if nat == None:
                ret = Q_LOCAL % (msg_key, msg_key, local_no, self.sms_sender, 
                                 subject, body)
            else:
                if len(subject) > 80:
                    subject = subject[:77] + "..."
                    
                ret = Q_NAT % (msg_key, local_no, self.sms_sender, subject, 
                               nat)
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
        
        # message example.
        #
        #    {'body': u'Threshold Crossed: 3 datapoints were greater than the 
        #               threshold(50.000000). The most recent datapoints: 
        #               [110.0, 110.0, 60.0]. at 2012-08-28T10:17:50.494902',
        #     'receivers': [u'+82 1093145616'],
        #     'method': 'SMS',
        #     'subject': u'AlarmActionTest state has been changed from OK to
        #                  ALARM at 2012-08-28T10:17:50.494902'}
        #
    
        LOG.debug("Connect to mysql db %s@%s:%s %s" % (self.sms_db_username,
                            self.sms_db_host, self.sms_db_port, self.sms_db))
        conn = db.connect(host=self.sms_db_host, port=self.sms_db_port, 
                          db=self.sms_db, user=self.sms_db_username, 
                          passwd=self.sms_db_password, connect_timeout=30,
                          charset='utf8')
        c = conn.cursor()
        for receiver in message['receivers']:
            q = build_query(receiver, message)
            c.execute(q)
        
        c.close()
        conn.commit()
        conn.close()
        
    
    def send_email(self, message):
        msg = MIMEText(message['body'], 'plain', 'utf8')
        msg['Subject'] = message['subject']
        msg['From'] = self.mail_sender
        msg['To'] = ", ".join(message['receivers'])
        
        s = smtplib.SMTP(self.smtp_server, timeout=30)
        s.sendmail(self.mail_sender, message['receivers'], msg.as_string())
        s.quit()
    
    
    def process(self, tup):
        self.process_action(tup)
