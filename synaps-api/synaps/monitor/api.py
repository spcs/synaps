# -*- coding:utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 Piston Cloud Computing, Inc.
# Copyright 2012 Red Hat, Inc.
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

import json
import uuid

from pandas import TimeSeries, DataFrame, DateRange, datetools
from pandas import (rolling_sum, rolling_max, rolling_min, rolling_mean)

from synaps import flags
from synaps import log as logging
from synaps.db import Cassandra
from synaps import rpc
from synaps import utils
from synaps.exception import (AdminRequired, InvalidRequest, ResourceNotFound,
                              InvalidParameterValue)

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS    

class API(object):
    ROLLING_FUNC_MAP = {
        'Average': rolling_mean, 'Minimum': rolling_min,
        'Maximum': rolling_max, 'SampleCount': rolling_sum,
        'Sum': rolling_sum,
    }
    
    def __init__(self):
        self.cass = Cassandra()
        self.rpc = rpc.RemoteProcedureCall()

    def delete_alarms(self, project_id, alarm_names):
        alarmkeys = []
        for alarm_name in alarm_names:
            k = self.cass.get_metric_alarm_key(project_id, alarm_name)
            if not k:
                raise ResourceNotFound("Alarm %s does not exists." % 
                                       alarm_name)
            alarmkeys.append(str(k))
                
        body = {'project_id': project_id, 'alarmkeys': alarmkeys} # UUID str  
        self.rpc.send_msg(rpc.DELETE_ALARMS_MSG_ID, body)
        LOG.info("DELETE_ALARMS_MSG sent")
        

    def describe_alarms(self, project_id, action_prefix=None,
                        alarm_name_prefix=None, alarm_names=None,
                        max_records=None, next_token=None, state_value=None):
        """
        params:
            project_id: string
            action_prefix: TODO: not implemented yet.
            alarm_name_prefix: string
            alarm_names: string list
            max_records: integer
            next_token: string (uuid type)
            state_value: string (OK | ALARM | INSUFFICIENT_DATA)
        """

        alarms = self.cass.describe_alarms(project_id, action_prefix,
                                           alarm_name_prefix, alarm_names,
                                           max_records, next_token,
                                           state_value)
        return alarms
    
    def describe_alarms_for_metric(self, project_id, namespace, metric_name,
                                   dimensions=None, period=None,
                                   statistic=None, unit=None):
        """
        params:
            project_id: string
            metric_name: string
            namespace: string
            dimensions: dict
            period: integer
            statistic: string (SampleCount | Average | Sum | Minimum | 
                               Maximum)
            unit: string
        """
        alarms = self.cass.describe_alarms_for_metric(project_id, namespace,
            metric_name, dimensions=dimensions, period=period,
            statistic=statistic, unit=unit)
        return alarms

    def describe_alarm_history(self, project_id, alarm_name=None,
                               end_date=None, history_item_type=None,
                               max_records=None, next_token=None,
                               start_date=None):
        histories = self.cass.describe_alarm_history(
            alarm_name=alarm_name, end_date=end_date,
            history_item_type=history_item_type,
            max_records=max_records, next_token=next_token,
            start_date=start_date, project_id=project_id
        )
        return histories
    
    def set_alarm_actions(self, project_id, alarm_names, enabled):
        for alarm_name in alarm_names:
            alarm_key = self.cass.get_metric_alarm_key(project_id, alarm_name)
            self.cass.put_metric_alarm(alarm_key, {'actions_enabled':enabled})
    
    def set_alarm_state(self, project_id, alarm_name, state_reason,
                        state_value, state_reason_data=None):

        k = self.cass.get_metric_alarm_key(project_id, alarm_name)
        if not k:
            raise ResourceNotFound("Alarm %s does not exists." % alarm_name)
       
        body = {'project_id': project_id, 'alarm_name': alarm_name,
                'state_reason': state_reason, 'state_value': state_value,
                'state_reason_data': state_reason_data}   
        self.rpc.send_msg(rpc.SET_ALARM_STATE_MSG_ID, body)
        LOG.info("SET_ALARM_STATE_MSG sent")        
    
    def get_metric_statistics(self, project_id, end_time, metric_name,
                              namespace, period, start_time, statistics,
                              unit=None, dimensions=None):
        """
        입력받은 조건에 일치하는 메트릭의 통계자료 리스트를 반환한다.
        """
        def to_datapoint(df, idx):
            datapoint = df.ix[idx].dropna()
            if len(datapoint):
                return idx, datapoint
        
        end_idx = end_time.replace(second=0, microsecond=0)
        start_idx = start_time.replace(second=0, microsecond=0)
        start_ana_idx = start_idx - datetools.Minute() * (period / 60)
        daterange = DateRange(start_idx, end_idx, offset=datetools.Minute())
        daterange_ana = DateRange(start_ana_idx, end_idx,
                                  offset=datetools.Minute())

        # load default unit for metric from database
        if unit == "None" or not unit:
            metric_key = self.cass.get_metric_key(
                project_id=project_id, namespace=namespace,
                metric_name=metric_name, dimensions=dimensions
            )
            
            if metric_key:
                unit = self.cass.get_metric_unit(metric_key)
            else:
                unit = "None"
        
        # load statistics data from database
        stats = self.cass.get_metric_statistics(
            project_id=project_id, namespace=namespace,
            metric_name=metric_name, start_time=start_ana_idx,
            end_time=end_time, period=period, statistics=statistics,
            dimensions=dimensions
        )
        
        period = period / 60 # convert sec to min
        stat = DataFrame(index=daterange)
        
        for statistic, series in zip(statistics, stats):
            func = self.ROLLING_FUNC_MAP[statistic]
            if statistic == 'SampleCount':
                ts = TimeSeries(series, index=daterange_ana).fillna(0)
            else:
                ts = TimeSeries(series, index=daterange_ana)
            stat[statistic] = func(ts, period, min_periods=0)

        ret = filter(None, (to_datapoint(stat, i) for i in stat.index))
        return ret

    def list_metrics(self, project_id, next_token=None, dimensions=None,
                     metric_name=None, namespace=None):
        """
        입력받은 조건과 일치하는 메트릭의 리스트를 반환한다.
        """
        metrics = self.cass.list_metrics(project_id, namespace, metric_name,
                                         dimensions, next_token)
        return metrics
    
    def put_metric_alarm(self, project_id, metricalarm):
        """
        알람을 DB에 넣고 값이 빈 dictionary 를 반환한다.
        메트릭 유무 확인
        알람 히스토리 발생.
        """
        def metricalarm_for_json(metricalarm):
            alarm_for_json = {
                'actionEnabled': metricalarm.get('actions_enabled', False),
                'alarmActions': metricalarm.get('alarm_actions', []),
                'alarmArn': metricalarm.get('alarm_arn'),
                'alarmConfigurationUpdatedTimestamp': 
                      metricalarm.get('alarm_configuration_updated_timestamp'),
                'alarmDescription': metricalarm.get('alarm_description'),
                'alarmName': metricalarm.get('alarm_name'),
                'comparisonOperator': metricalarm.get('comparison_operator'),
                'dimensions': metricalarm.get('dimensions'),
                'evaluationPeriods': metricalarm.get('evaluation_periods'),
                'insufficientDataActions': 
                    metricalarm.get('insufficient_data_actions', []),
                'metricName':metricalarm.get('metric_name'),
                'namespace':metricalarm.get('namespace'),
                'okactions':metricalarm.get('ok_actions', []),
                'statistic':metricalarm.get('statistic'),
                'threshold':metricalarm.get('threshold'),
                'unit':metricalarm.get('unit'),
            }
            return alarm_for_json

        now = utils.utcnow()
        metricalarm = metricalarm.to_columns()
        
        # 메트릭 유무 확인
        metric_key = self.cass.get_metric_key_or_create(
            project_id=project_id,
            namespace=metricalarm['namespace'],
            metric_name=metricalarm['metric_name'],
            dimensions=json.loads(metricalarm['dimensions']),
            unit=metricalarm['unit'],
        )
        
        metricalarm['project_id'] = project_id
        metricalarm['metric_key'] = metric_key
        metricalarm['alarm_arn'] = "arn:spcs:synaps:%s:alarm:%s" % (
            project_id, metricalarm['alarm_name']
        )
        metricalarm['alarm_configuration_updated_timestamp'] = now
        
        # 알람 유무 확인
        alarm_key = self.cass.get_metric_alarm_key(
            project_id=project_id, alarm_name=metricalarm['alarm_name']
        )
        
        
        if alarm_key:            
            history_type = 'Update'
            before_alarm = self.cass.get_metric_alarm(alarm_key)
            if before_alarm['metric_key'] != metricalarm['metric_key']:
                raise InvalidRequest("Metric cannot be changed.")
            
            metricalarm['state_updated_timestamp'] = \
                before_alarm['state_updated_timestamp']
            metricalarm['state_reason'] = before_alarm['state_reason']
            metricalarm['state_reason_data'] = \
                before_alarm['state_reason_data']
            metricalarm['state_value'] = before_alarm['state_value']
            
        else:            
            history_type = "Create"
            alarm_key = uuid.uuid4()
            metricalarm['state_updated_timestamp'] = utils.utcnow()
            metricalarm['state_reason'] = "Unchecked: Initial alarm creation"
            metricalarm['state_reason_data'] = json.dumps({})
            metricalarm['state_value'] = "INSUFFICIENT_DATA"
            
        
        # insert alarm into database
        self.cass.put_metric_alarm(alarm_key, metricalarm)
        LOG.debug("metric alarm inserted alarm key: %s" % (alarm_key))

        # to make json, convert datetime type into str        
        metricalarm['state_updated_timestamp'] = utils.strtime(
            metricalarm['state_updated_timestamp']
        )
        metricalarm['alarm_configuration_updated_timestamp'] = utils.strtime(
            metricalarm['alarm_configuration_updated_timestamp']
        )
        metricalarm['metric_key'] = str(metric_key)
        
        if history_type == "Update":
            history_data = json.dumps({
                'updatedAlarm':metricalarm_for_json(metricalarm),
                'type':history_type,
                'version': '1.0'
            })
            summary = "Alarm %s updated" % metricalarm['alarm_name']
        else:
            history_data = json.dumps({
                'createdAlarm': metricalarm_for_json(metricalarm),
                'type':history_type, 'version': '1.0'
            })
            summary = "Alarm %s created" % metricalarm['alarm_name']
        
        history_key = uuid.uuid4()
        history_column = {
            'project_id': project_id,
            'alarm_key': alarm_key,
            'alarm_name': metricalarm['alarm_name'],
            'history_data': history_data,
            'history_item_type': 'ConfigurationUpdate',
            'history_summary':summary,
            'timestamp': utils.utcnow()
        }
            
        self.cass.insert_alarm_history(history_key, history_column)
        
        message = {'project_id': project_id, 'metric_key': str(metric_key),
                   'metricalarm': metricalarm}
        self.rpc.send_msg(rpc.PUT_METRIC_ALARM_MSG_ID, message)
        LOG.info("PUT_METRIC_ALARM_MSG sent")

        return {}
    
    def put_metric_data(self, project_id, namespace, metric_name, dimensions,
                        value, unit, timestamp, is_admin=False):
        """
        metric data 를 입력받아 MQ 에 넣고 값이 빈 dictionary 를 반환한다.        
        """
        if namespace.startswith("SPCS/") and not is_admin:
            raise AdminRequired()

        message = {'project_id': project_id, 'namespace':namespace,
                   'metric_name': metric_name, 'dimensions': dimensions,
                   'value':value, 'unit':unit, 'timestamp':timestamp}
        
        self.rpc.send_msg(rpc.PUT_METRIC_DATA_MSG_ID, message)
        LOG.info("PUT_METRIC_DATA_MSG sent")
            
        return {}
