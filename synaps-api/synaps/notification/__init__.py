#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright (c) 2012 Samsung SDS Co., LTD
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import os
import sys
import smtplib
import MySQLdb as db
from email.mime.text import MIMEText
from synaps import flags
from synaps import log as logging
from synaps import utils
from uuid import uuid4

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS

SMTP_SERVER = FLAGS.get('smtp_server')
MAIL_SENDER = FLAGS.get('mail_sender')
SMS_SENDER = FLAGS.get('sms_sender')
SMS_DB_HOST = FLAGS.get('sms_database_host')
SMS_DB_PORT = FLAGS.get('sms_database_port')
SMS_DB = FLAGS.get('sms_database')
SMS_DB_USERNAME = FLAGS.get('sms_db_username')
SMS_DB_PASSWORD = FLAGS.get('sms_db_password')

def send_sms(message):
    Q_LOCAL = """insert into SMS_SEND(REG_TIME, MSG_KEY, RECEIVER, SENDER, 
    MESSAGE) values (now()+0, '%s','%s','%s','%s')
    """
    Q_NAT = """insert into SMS_SEND(REG_TIME, MSG_KEY, RECEIVER, SENDER, 
    MESSAGE, NAT_CODE) values (now()+0, '%s','%s','%s','%s', %d)
    """

    def build_query(receiver, subject):
        nat, local_no = parse_number(receiver)
        if nat == None:
            ret = Q_LOCAL % (str(uuid4())[:15], local_no, SMS_SENDER,
                             subject[:80])
        else:
            ret = Q_NAT % (str(uuid4())[:15], local_no, SMS_SENDER,
                           subject[:80], nat)
        return ret
        
    def parse_number(no):
        nat, local_no = no.split(' ', 1)
        if nat.startswith("+"):
            nat = int(nat[1:])
        else:
            nat = int(nat)
        
        if nat == 82: # Korean national code
            nat = None
            local_no = '0' + local_no.replace(' ', '')
        else:
            local_no = local_no.replace(' ', '')
        
        return nat, local_no
    
    LOG.info("SMS: %s" % str(message))
    
    # message example.
    #
    #    {'body': u'Threshold Crossed: 3 datapoints were greater than the threshold(50.000000). The most recent datapoints: [110.0, 110.0, 60.0]. at 2012-08-28T10:17:50.494902',
    #     'receivers': [u'+82 1093145616'],
    #     'method': 'SMS',
    #     'subject': u'AlarmActionTest state has been changed from OK to ALARM at 2012-08-28T10:17:50.494902'}
    #

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
    

def send_email(message):
    LOG.info("EMAIL: %s" % str(message))

    msg = MIMEText(message['body'])
    msg['Subject'] = message['subject']
    msg['From'] = MAIL_SENDER
    msg['To'] = ", ".join(message['receivers'])
    
    s = smtplib.SMTP(SMTP_SERVER, timeout=30)
    s.sendmail(MAIL_SENDER, message['receivers'], msg.as_string())
    s.quit()

