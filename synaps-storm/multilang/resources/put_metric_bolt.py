# -*- coding:utf-8 -*-

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
import operator
import time
from uuid import uuid4, UUID

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "synaps", "__init__.py")):
    sys.path.insert(0, possible_topdir)

import traceback
import storm
import json
import uuid

from datetime import datetime, timedelta
from pandas import TimeSeries, DataFrame, DateRange, datetools
from pandas import rolling_sum, rolling_max, rolling_min, rolling_mean
from numpy import isnan

from synaps import flags
from synaps import log as logging
from synaps import utils
from synaps.db import Cassandra
from synaps.rpc import (PUT_METRIC_DATA_MSG_ID, PUT_METRIC_ALARM_MSG_ID,
                        DELETE_ALARMS_MSG_ID, SET_ALARM_STATE_MSG_ID,
                        CHECK_METRIC_ALARM_MSG_ID)
from synaps import exception

FLAGS = flags.FLAGS
flags.FLAGS(sys.argv)
utils.default_flagfile()
logging.setup()
    
class MetricMonitor(object):
    COLUMNS = Cassandra.STATISTICS
    STATISTICS_TTL = Cassandra.STATISTICS_TTL
    MAX_START_PERIOD = FLAGS.get('max_start_period')
    MIN_START_PERIOD = 0
    MAX_END_PERIOD = FLAGS.get('max_end_period')
        
    ROLLING_FUNC_MAP = {
        'Average': rolling_mean,
        'Minimum': rolling_min,
        'Maximum': rolling_max,
        'SampleCount': rolling_sum,
        'Sum': rolling_sum,
    }
    
    CMP_MAP = {
        'GreaterThanOrEqualToThreshold':  operator.ge,
        'GreaterThanThreshold': operator.gt,
        'LessThanThreshold': operator.lt,
        'LessThanOrEqualToThreshold': operator.le,
    }

    CMP_STR_MAP = {
        'GreaterThanOrEqualToThreshold': "greater than or equal to",
        'GreaterThanThreshold': "greater than",
        'LessThanThreshold': "less than",
        'LessThanOrEqualToThreshold': "less than or equal to",
    }    
    
    
    def __init__(self, metric_key, cass):
        self.metric_key = metric_key
        self.cass = cass
        self.df = self.load_statistics()
        self.alarms = self.load_alarms()
        self.set_max_start_period(self.alarms)
        self._reindex()

        self.lastchecked = None
        
    def _reindex(self):
        self.df = self.df.reindex(index=self._get_range())
        
    def _get_range(self):
        now_idx = datetime.utcnow().replace(second=0, microsecond=0)

        start = now_idx - timedelta(seconds=self.MAX_START_PERIOD)
        end = now_idx + timedelta(seconds=self.MAX_END_PERIOD)

        daterange = DateRange(start, end, offset=datetools.Minute())
        
        return daterange
    

    def set_max_start_period(self, alarms):
        msp = self.MAX_START_PERIOD
        
        try:
            self.MAX_START_PERIOD = max(v.get('period') for v 
                                        in alarms.itervalues()) \
                                    if alarms else FLAGS.get('max_start_period') 
            self.MIN_START_PERIOD = min(v.get('period') for v 
                                        in alarms.itervalues()) \
                                    if alarms else 0
        except AttributeError:
            msg = "alarm is not found in alarms."
            self.log(msg)
            
            return False 
                  
        msg = "MAX_START_PERIOD is changed %s -> %s"                 
        storm.log(msg % (str(msp), self.MAX_START_PERIOD))

        if msp < self.MAX_START_PERIOD:
            self.df = self.load_statistics()
        elif msp > self.MAX_START_PERIOD:
            self._reindex()
                
    def delete_metric_alarm(self, alarmkey):
        """
        메모리 및 DB에서 알람을 삭제한다.
        
        alarmkey:
            alarmkey should be UUID
        """
        try:
            alarm = self.alarms.pop(alarmkey)
        except KeyError:
            storm.log("alarmkey %s doesn't exist" % alarmkey)
            return
        
        self.cass.delete_metric_alarm(alarmkey)
        self.alarm_history_delete(alarmkey, alarm)
        storm.log("delete alarm %s for metric %s" % (str(alarmkey),
                                                     self.metric_key))
        

        self.set_max_start_period(self.alarms)        
        

    def load_statistics(self):
        now_idx = datetime.utcnow().replace(second=0, microsecond=0)
        start = now_idx - timedelta(seconds=self.MAX_START_PERIOD)
        end = now_idx + timedelta(seconds=self.MAX_END_PERIOD)
        
        stat = self.cass.load_statistics(self.metric_key, start, end)
        
        if stat:
            df = DataFrame(stat, index=self._get_range())
        else:
            df = DataFrame(columns=self.COLUMNS, index=self._get_range())
        return df
    
    def load_alarms(self):
        alarms = dict(self.cass.load_alarms(self.metric_key))
        storm.log("load_alarms %s for metric %s" % (str(alarms),
                                                    self.metric_key))
        return alarms

    def get_metric_statistics(self, window, statistics, start=None, end=None,
                              unit=None):
        
        df = self.df.ix[start:end] if start and end else self.df
        
        ret_dict = {}
        for statistic in statistics:
            func = self.ROLLING_FUNC_MAP[statistic]
            ret_dict[statistic] = func(df[statistic], window)
        
        return DataFrame(ret_dict)
    
    def put_alarm(self, project_id, metricalarm):
        alarm_name = metricalarm.get('alarm_name')
        alarm_key = self.cass.get_metric_alarm_key(project_id, alarm_name)
        if alarm_key:
            ret = self.cass.get_metric_alarm(alarm_key)
            if ret:
                self.alarms[alarm_key] = ret
                storm.log("alarm key is [%s]" % alarm_key)
                self.set_max_start_period(self.alarms)
            else:
                storm.log("alarm key [%s] is found, but alarm is not found." % alarm_key)
        else:
            storm.log("no alarm key [%s]" % alarm_key)        
        
    def put_metric_data(self, metric_key, timestamp, value, unit=None):
        
        def get_stats(tmp_stat):
            try:
                ret = dict(zip(self.cass.STATISTICS,
                                    map(lambda x: x.values()[0], tmp_stat)))
                for v in ret:
                    if v == None: v = float('nan') 
            except IndexError:
                storm.log("index %s is not in DB." % time_idx)
                ret = {'SampleCount' : float('nan'),
                        'Sum' : float('nan'),
                        'Average' : float('nan'),
                        'Minimum' : float('nan'),
                        'Maximum' : float('nan') }
            return ret
        
                 
        time_idx = timestamp.replace(second=0, microsecond=0)
        
        if timedelta(seconds=self.cass.STATISTICS_TTL) < (utils.utcnow() - 
                                                            time_idx):
            msg = "index %s is older than TTL. It doesn't need to insert DB"
            storm.log(msg % time_idx)
            return
        
        
        if time_idx not in self.df.index:
            self._reindex()
        
        value = utils.to_default_unit(value, unit)
        
        try:
            stat = self.df.ix[time_idx]
            
            for v in stat:
                if v == None: v = float('nan')                    
                 
        except KeyError:
            stat = self.cass.get_metric_statistics_for_key(metric_key, time_idx)
            stat = get_stats(stat)

        
        stat['SampleCount'] = 1.0 if isnan(stat['SampleCount']) \
                              else stat['SampleCount'] + 1.0
        stat['Sum'] = value if isnan(stat['Sum'])  \
                      else stat['Sum'] + value
        stat['Average'] = stat['Sum'] / stat['SampleCount']
        stat['Minimum'] = value \
                          if isnan(stat['Minimum']) or stat['Minimum'] > value \
                          else stat['Minimum']
        stat['Maximum'] = value \
                          if isnan(stat['Maximum']) or stat['Maximum'] < value \
                          else stat['Maximum']

        # insert into DB
        stat_dict = {
            'SampleCount':{time_idx: stat['SampleCount']},
            'Sum':{time_idx: stat['Sum']},
            'Average':{time_idx: stat['Average']},
            'Minimum':{time_idx: stat['Minimum']},
            'Maximum':{time_idx: stat['Maximum']}
        }        
        
        self.cass.insert_stat(self.metric_key, stat_dict)
        storm.log("metric data inserted %s" % (self.metric_key))
        
        #self.df.ix[time_idx] = stat
        
        now = utils.utcnow().replace(second=0, microsecond=0)
        timedelta_buf = now - time_idx
        
        if(timedelta_buf <= timedelta(seconds=self.MAX_START_PERIOD)):
            # check alarms
            self.check_alarms()
        

                
    
    def check_alarms(self):
        for alarmkey, alarm in self.alarms.iteritems():
            self._check_alarm(alarmkey, alarm)
        self.lastchecked = utils.utcnow()
            
    def _check_alarm(self, alarmkey, alarm):
        period = int(alarm['period'] / 60)
        evaluation_periods = alarm['evaluation_periods']
        statistic = alarm['statistic']
        threshold = alarm['threshold']
        cmp_op = self.CMP_MAP[alarm['comparison_operator']]
        unit = alarm['unit']
        state_value = alarm['state_value']
        
        now = utils.utcnow()
        end_idx = now.replace(second=0, microsecond=0) - datetools.Minute()
        start_idx = end_idx - (evaluation_periods - 1) * datetools.Minute()
        start_ana_idx = start_idx - datetools.Minute() * period
        
        func = self.ROLLING_FUNC_MAP[statistic]
        data = func(self.df[statistic].ix[start_ana_idx:end_idx], period,
                    min_periods=0).ix[start_idx:end_idx]
                      
        if statistic == 'SampleCount':
            data = data.fillna(0)
        else:
            if unit:
                data = data / utils.UNIT_CONV_MAP[unit]
                threshold = threshold / utils.UNIT_CONV_MAP[unit]
                
            data = data.dropna()

        query_date = utils.strtime(now)
        reason_data = {
            "period":alarm['period'],
            "queryDate":query_date,
            "recentDatapoints": list(data),
            "startDate": utils.strtime(start_idx),
            "statistic":statistic,
            "threshold": threshold,
            "version":"1.0",
        }
        old_state = {'stateReason':alarm.get('reason', ""),
                     'stateValue':alarm.get('state_value',
                                            "INSUFFICIENT_DATA"),
                     'stateReasonData':
                        json.loads(alarm.get('reason_data', "{}"))}
        json_reason_data = json.dumps(reason_data)

        if len(data) < evaluation_periods:
            if state_value != 'INSUFFICIENT_DATA':
                template = _("Insufficient Data: %d datapoints were unknown.")
                reason = template % (evaluation_periods - len(data))
                new_state = {'stateReason':reason,
                             'stateReasonData':reason_data,
                             'stateValue':'INSUFFICIENT_DATA'}
                self.update_alarm_state(alarmkey, 'INSUFFICIENT_DATA', reason,
                                        json_reason_data, now)
                self.cass.update_alarm_state(alarmkey, 'INSUFFICIENT_DATA',
                                             reason, json_reason_data, now)
                self.alarm_history_state_update(alarmkey, alarm,
                                                new_state, old_state)
                self.do_alarm_action(alarmkey, alarm, new_state, old_state,
                                     query_date)
                storm.log("INSUFFICIENT_DATA alarm")
        else:
            crossed = reduce(operator.and_, cmp_op(data, threshold))
            com_op = alarm['comparison_operator']
            
            if crossed:
                template = _("Threshold Crossed: %d datapoints were %s " + 
                             "the threshold(%f). " + 
                             "The most recent datapoints: %s.")
                reason = template % (len(data),
                                     self.CMP_STR_MAP[com_op],
                                     threshold, str(list(data)))
                if state_value != 'ALARM':
                    new_state = {'stateReason':reason,
                                 'stateReasonData':reason_data,
                                 'stateValue':'ALARM'}
                    
                    self.update_alarm_state(alarmkey, 'ALARM', reason,
                                            json_reason_data, now)
                    self.cass.update_alarm_state(alarmkey, 'ALARM', reason,
                                                 json_reason_data, now)
                    self.alarm_history_state_update(alarmkey, alarm,
                                                    new_state, old_state)
                    self.do_alarm_action(alarmkey, alarm, new_state, old_state,
                                         query_date)                    
                    storm.log("ALARM alarm")
            else:
                template = _("Threshold Crossed: %d datapoints were not %s " + 
                             "the threshold(%f). " + 
                             "The most recent datapoints: %s.")
                reason = template % (len(data),
                                     self.CMP_STR_MAP[com_op],
                                     threshold, str(list(data)))
                if state_value != 'OK':
                    new_state = {'stateReason':reason,
                                 'stateReasonData':reason_data,
                                 'stateValue':'OK'}                    
                    self.update_alarm_state(alarmkey, 'OK', reason,
                                            json_reason_data, now)
                    self.cass.update_alarm_state(alarmkey, 'OK', reason,
                                                 json_reason_data, now)
                    self.alarm_history_state_update(alarmkey, alarm,
                                                    new_state, old_state)
                    self.do_alarm_action(alarmkey, alarm, new_state, old_state,
                                         query_date)                            
                    storm.log("OK alarm")
            
    
    def do_alarm_action(self, alarmkey, alarm, new_state, old_state,
                        query_date):
        """
        parameter example:
        
        alarmkey: f459c0e0-f927-481f-9158-deb8abe102a2 
        alarm: OrderedDict([('actions_enabled', False), 
                            ('alarm_actions', u'[]'), 
                            ('alarm_arn', u'arn:spcs:synaps:IaaS:alarm:TEST_\uc54c\ub78c_02'), 
                            ('alarm_configuration_updated_timestamp', datetime.datetime(2012, 8, 25, 10, 51, 38, 469000)), 
                            ('alarm_description', u''), 
                            ('alarm_name', u'TEST_\uc54c\ub78c_02'), 
                            ('comparison_operator', u'LessThanThreshold'), 
                            ('dimensions', u'{"instance_name": "test instance"}'), 
                            ('evaluation_periods', 2), 
                            ('insufficient_data_actions', u'[]'), 
                            ('metric_key', UUID('96f19ec9-673b-4237-ae66-1bfde526595c')), 
                            ('metric_name', u'test_metric'), 
                            ('namespace', u'SPCS/SYNAPSTEST'), 
                            ('ok_actions', u'[]'), 
                            ('period', 300), 
                            ('project_id', u'IaaS'), 
                            ('state_reason', u'Threshold Crossed: 2 datapoints were not less than the threshold(2.000000). The most recent datapoints: [55.25, 55.25].'), 
                            ('state_reason_data', u'{"startDate": "2012-08-25T10:30:00.000000", "period": 300, "threshold": 2.0, "version": "1.0", "statistic": "Average", "recentDatapoints": [55.25, 55.25], "queryDate": "2012-08-25T10:32:24.671991"}'), 
                            ('state_updated_timestamp', datetime.datetime(2012, 8, 25, 11, 39, 49, 657449)), 
                            ('state_value', 'OK'), 
                            ('statistic', u'Average'), 
                            ('threshold', 2.0), 
                            ('unit', u'Percent'), 
                            ('reason', u'Threshold Crossed: 3 datapoints were not less than the threshold(2.000000). The most recent datapoints: [75.0, 80.0, 67.625].'), 
                            ('reason_data', '{"startDate": "2012-08-25T11:37:00.000000", "period": 300, "threshold": 2.0, "version": "1.0", "statistic": "Average", "recentDatapoints": [75.0, 80.0, 67.625], "queryDate": "2012-08-25T11:39:49.657449"}')
                            ]) 
        new_state: {'stateReason': u'Threshold Crossed: 3 datapoints were not less than the threshold(2.000000). The most recent datapoints: [75.0, 80.0, 67.625].', 
                    'stateValue': 'OK', 
                    'stateReasonData': {'startDate': '2012-08-25T11:37:00.000000', 'period': 300, 'threshold': 2.0, 'version': '1.0', 'statistic': u'Average', 'recentDatapoints': [75.0, 80.0, 67.625], 'queryDate': '2012-08-25T11:39:49.657449'}} 
        old_state: {'stateReason': u'Insufficient Data: 1 datapoints were unknown.', 
                    'stateReasonData': {u'startDate': u'2012-08-25T11:37:00.000000', u'period': 300, u'recentDatapoints': [55.25], u'version': u'1.0', u'statistic': u'Average', u'threshold': 2.0, u'queryDate': u'2012-08-25T11:39:26.261056'}, 'stateValue': 'INSUFFICIENT_DATA'}
        """

        msg = {
            'state': new_state['stateValue'],
            'subject': "%s state has been changed from %s to %s at %s" % 
                (alarm['alarm_name'], old_state['stateValue'],
                 new_state['stateValue'], query_date),
            'body': "%s at %s" % (new_state['stateReason'], query_date),
            'query_date': query_date
        }
        storm.log("emit to Alarm Action: %s %s" % (alarmkey, msg)) 
        storm.emit([str(alarmkey), json.dumps(msg)])        
    
    def alarm_history_delete(self, alarm_key, alarm):
        item_type = 'ConfigurationUpdate'
        summary = "Alarm %s deleted" % alarm['alarm_name']
        
        history_key = uuid.uuid4()
        history_column = {
            'project_id': alarm['project_id'],
            'alarm_key': alarm_key,
            'alarm_name': alarm['alarm_name'],
            'history_data': json.dumps({'type': 'Delete', 'version': '1.0'}),
            'history_item_type': item_type,
            'history_summary': summary,
            'timestamp': utils.utcnow()
        }
        
        self.cass.insert_alarm_history(history_key, history_column)
        
    
    def alarm_history_state_update(self, alarmkey, alarm, new_state,
                                          old_state):
        item_type = 'StateUpdate'
        project_id = alarm['project_id']
        summary_tpl = "Alarm updated from %s to %s" 
        summary = summary_tpl % (old_state.get('stateValue',
                                               'INSUFFICIENT_DATA'),
                                 new_state.get('stateValue',
                                               'INSUFFICIENT_DATA'))
        timestamp = utils.utcnow()
        data = {'newState':new_state, 'oldState':old_state, 'version':'1.0'}

        history_key = uuid.uuid4()
        column = {'project_id':project_id, 'alarm_key':alarmkey,
                  'alarm_name':alarm['alarm_name'],
                  'history_data':json.dumps(data),
                  'history_item_type':item_type, 'history_summary':summary,
                  'timestamp':timestamp}
        
        self.cass.insert_alarm_history(history_key, column)
        storm.log("alarm history \n %s" % summary)
                
    def update_alarm_state(self, alarmkey, state_value, reason, reason_data,
                           timestamp):
        alarm = self.alarms[alarmkey]
        alarm['state_value'] = state_value
        alarm['reason'] = reason
        alarm['reason_data'] = reason_data
        alarm['state_updated_timestamp'] = timestamp        
            

class PutMetricBolt(storm.BasicBolt):
    BOLT_NAME = "PutMetricBolt"
    
    def initialize(self, stormconf, context):
        self.cass = Cassandra()
        self.metrics = {}
    
    def log(self, msg):
        storm.log("[%s] %s" % (self.BOLT_NAME, msg))
        
    def tracelog(self, e):
        msg = traceback.format_exc(e)
        for line in msg.splitlines():
            self.log("TRACE: " + line)
    
    def process_put_metric_data_msg(self, metric_key, message):
        """
        데이터베이스에 MetricArchive 컬럼패밀리에 입력된 값 추가. 메모리
        (self.metrics)에도 입력된 값 추가.
        
        메모리 상의 메트릭을 기반으로 데이터베이스에 StatArchive 컬럼패밀리 
        업데이트.
        """
        # 메시지 값이 없는 경우 종료    
        if message['value'] is None:
            return
        
        # 메트릭 가져오기
        if metric_key not in self.metrics:
            self.metrics[metric_key] = MetricMonitor(metric_key, self.cass)

        timestamp = utils.parse_strtime(message['timestamp'])


        self.metrics[metric_key].put_metric_data(metric_key,
                                                 timestamp=timestamp,
                                                 value=message['value'],
                                                 unit=message['unit'])
    
    def process_put_metric_alarm_msg(self, metric_key, message):
        if metric_key not in self.metrics:
            self.metrics[metric_key] = MetricMonitor(metric_key, self.cass)
        project_id = message['project_id']
        metricalarm = message['metricalarm']
        self.metrics[metric_key].put_alarm(project_id, metricalarm)

    def process_delete_metric_alarms_msg(self, metric_key, message):
        alarmkey = UUID(message['alarmkey'])
        self.log("debug: %s" % self.metrics.keys())
        if metric_key not in self.metrics:
            self.metrics[metric_key] = MetricMonitor(metric_key, self.cass)
        self.metrics[metric_key].delete_metric_alarm(alarmkey)
        
    def process_set_alarm_state_msg(self, metric_key, message):
        project_id = message.get('project_id')
        alarm_name = message.get('alarm_name')
        state_reason_data = message.get('state_reason_data')
                      
        if metric_key not in self.metrics:
            self.metrics[metric_key] = MetricMonitor(metric_key, self.cass)

        metric = self.metrics[metric_key]
        
        ret = self.cass.get_metric_alarm_key(project_id, alarm_name)
        if ret:
            alarm_key = ret
            try:
                metricalarm = metric.alarms[alarm_key]
            except KeyError:
                storm.log("alarm key [%s] is found, but alarm is not found." % alarm_key)
                return            
        else:
            storm.log("alarm key [%s] is not found." % alarm_key)
            return
        
        metricalarm['state_reason'] = message.get('state_reason')
        metricalarm['state_value'] = message.get('state_value')
        metricalarm['state_reason_data'] = message.get('state_reason_data')

        # write into database
        alarm_columns = {'state_reason':message.get('state_reason'),
                         'state_value':message.get('state_value')}
        if state_reason_data:
            alarm_columns['state_reason_data'] = state_reason_data
        
        self.cass.put_metric_alarm(alarm_key, alarm_columns)
        
    def process_check_metric_alarms_msg(self):
        now = datetime.utcnow()

        for metric in self.metrics.itervalues():
            min_start_period = timedelta(seconds=metric.MIN_START_PERIOD)

            if ((metric.lastchecked and 
                 (now - metric.lastchecked > min_start_period))
                or (metric.lastchecked == None)):
                metric.check_alarms()
        
    def process(self, tup):
        try:
            metric_key = UUID(tup.values[0]) if tup.values[0] else None
        except ValueError:
            self.log("badly formed hexadecimal UUID string - %s" % 
                     tup.values[0])
            return
        
        message = json.loads(tup.values[1])
        message_id = message.get('message_id')
        
        if message_id == PUT_METRIC_DATA_MSG_ID:
            self.log("process put_metric_data_msg (%s)" % message)
            self.process_put_metric_data_msg(metric_key, message)
        elif message_id == PUT_METRIC_ALARM_MSG_ID:
            self.log("process put_metric_alarm_msg (%s)" % message)
            self.process_put_metric_alarm_msg(metric_key, message)
        elif message_id == DELETE_ALARMS_MSG_ID:
            self.log("process put_metric_alarm_msg (%s)" % message)
            self.process_delete_metric_alarms_msg(metric_key, message)
        elif message_id == SET_ALARM_STATE_MSG_ID:
            self.log("process set_alarm_state_msg (%s)" % message)
            self.process_set_alarm_state_msg(metric_key, message)
        elif message_id == CHECK_METRIC_ALARM_MSG_ID:
            self.log("process check_metric_alarm_msg (%s)" % message)
            self.process_check_metric_alarms_msg()
        else:
            self.log("unknown message")

if __name__ == "__main__":
    PutMetricBolt().run()
