# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2012 Samsung SDS Co., LTD
# All Rights Reserved
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

import time
import datetime
from datetime import timedelta
import unittest
import random

from boto.ec2.cloudwatch.alarm import MetricAlarm
from boto.exception import BotoServerError

import synaps.tests
from synaps import flags
from synaps import log as logging
from synaps.tests import SynapsTestCase, attr

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS    

ASYNC_WAIT = 3


class AuthTest(SynapsTestCase):        
    @attr(type=['gate', 'negative'])
    def test_bad_access_key(self):
        self.assertRaises(BotoServerError, self.synaps_bad_ak.list_metrics)

    @attr(type=['gate', 'negative'])
    def test_bad_secret_key(self):
        self.assertRaises(BotoServerError, self.synaps_bad_sk.list_metrics)

    @attr(type=['gate'])
    def test_valid_keys(self):
        self.synaps.list_metrics()


class MetricTest(SynapsTestCase):
        
    @attr(type=['gate'])
    def test_put_metric_data(self):
        metric_name = self.generate_random_name("TestMetric_")
        now = datetime.datetime.utcnow()        
        now_idx = now.replace(second=0, microsecond=0)
        start_time = now - datetime.timedelta(hours=0.25)
        end_time = now

        ret = self.synaps.put_metric_data(
            namespace=self.namespace, name=metric_name,
            value=55.25, unit="Percent", dimensions=self.dimensions,
            timestamp=now_idx,
        )
        self.assertTrue(ret)

        time.sleep(ASYNC_WAIT)
        
        before_stat = self.synaps.get_metric_statistics(
            period=300, start_time=start_time, end_time=end_time,
            metric_name=metric_name, namespace=self.namespace,
            statistics=['Sum', 'Average', 'SampleCount'],
            dimensions=self.dimensions,
        )

        test_value = random.random() * 100
        
        
        ret = self.synaps.put_metric_data(
            namespace=self.namespace, name=metric_name,
            value=test_value, unit="Percent", dimensions=self.dimensions,
            timestamp=now_idx,
        )
        self.assertTrue(ret)

        time.sleep(ASYNC_WAIT)
        after_stat = self.synaps.get_metric_statistics(
            period=300, start_time=start_time, end_time=end_time,
            metric_name=metric_name, namespace=self.namespace,
            statistics=['Sum', 'Average', 'SampleCount'],
            dimensions=self.dimensions,
        )
        
        stat1 = filter(lambda x: x.get('Timestamp') == now_idx, before_stat)[0]
        stat2 = filter(lambda x: x.get('Timestamp') == now_idx, after_stat)[0]
        
        # expected = stat1['Sum'] + test_value
        self.assertAlmostEqual(stat1['Sum'] + test_value, stat2['Sum'])
        
        # expect that the unit matches that specified on the corresponding
        # PutMetricData call, even though we do not explicitly state the
        # in the GetMetricStatistics call
        self.assertEqual(stat2['Unit'], "Percent")

        # check 400 error when period is invalid
        test_period = 50
        try:
            self.synaps.get_metric_statistics(
                period=test_period, start_time=start_time, end_time=end_time,
                metric_name=metric_name, namespace=self.namespace,
                statistics=['Sum', 'Average', 'SampleCount'],
                dimensions=self.dimensions,
            )
        except BotoServerError as ex:
            self.assertEqual(ex.error_code, u'400')
        else:
            self.fail("should return 400 error")         

        test_period = 100
        try:
            self.synaps.get_metric_statistics(
                period=test_period, start_time=start_time, end_time=end_time,
                metric_name=metric_name, namespace=self.namespace,
                statistics=['Sum', 'Average', 'SampleCount'],
                dimensions=self.dimensions,
            )
        except BotoServerError as ex:
            self.assertEqual(ex.error_code, u'400')
        else:
            self.fail("should return 400 error")
            
                
    @attr(type='gate')
    def test_put_and_list_metrics(self):
        # put a metric and wait a seconds 
        metric_name = self.generate_random_name("TestListMetric-")
        self.synaps.put_metric_data(namespace=self.namespace, name=metric_name,
                                    dimensions=self.dimensions, value=0.0,
                                    timestamp=datetime.datetime.utcnow())
        time.sleep(ASYNC_WAIT)
        
        # check if the metric is exist
        ret = self.synaps.list_metrics(dimensions=self.dimensions,
                                       metric_name=metric_name,
                                       namespace=self.namespace)
        self.assertTrue(isinstance(ret, list))


    @attr(type=['negative', 'gate'])
    def test_put_numeric_metric(self):
        # When metric_name is number, it should be failed
        kwarg = {"namespace": self.namespace, "metric_name": "123456789",
                 "dimensions": None}
        self.assertRaises(BotoServerError, self.synaps.list_metrics, **kwarg)


    @attr(type=['gate', 'negative'])
    def test_put_metric_with_stale_timestamp(self):
        name_stale = self.generate_random_name("STALE_METRIC")
        name_fresh = self.generate_random_name("FRESH_METRIC")
        ttl = FLAGS.get('statistics_ttl')

        stale_time = (datetime.datetime.utcnow() - 
                      datetime.timedelta(seconds=ttl))

        # put metric at 'now - ttl' and get nothing
        kwargs = {'namespace': self.namespace, 'name': name_stale,
                  'value': 10.0, 'timestamp': stale_time}
        self.assertRaises(BotoServerError, self.synaps.put_metric_data,
                          **kwargs)
        
        # put metric at 'now - (ttl - 60)' and get one metric
        stale_time = (datetime.datetime.utcnow() - 
                      datetime.timedelta(seconds=ttl - 60))
        start_time = stale_time - datetime.timedelta(hours=1)
        end_time = stale_time + datetime.timedelta(hours=1)

        self.synaps.put_metric_data(namespace=self.namespace, name=name_fresh,
                                    value=10.0, timestamp=stale_time)
    
        time.sleep(ASYNC_WAIT)
        
        stat = self.synaps.get_metric_statistics(period=60,
                                                 start_time=start_time,
                                                 end_time=end_time,
                                                 metric_name=name_fresh,
                                                 namespace=self.namespace,
                                                 statistics=["Average"])
        self.assertEqual(1, len(stat))
        
        
class AlarmTest(SynapsTestCase):

    @attr(type=['gate', 'negative'])
    def test_put_metric_alarm_with_bad_statistic(self):
        # test check Parameters...
        alarmname = self.generate_random_name("BadAlarm")
        alarm = MetricAlarm(name=alarmname, metric=self.metric_name,
                            namespace=self.namespace,
                            statistic="It will occur an error",
                            comparison=">", threshold=50.0, period=300,
                            evaluation_periods=2, unit="Percent",
                            description=None, dimensions=self.dimensions,
                            alarm_actions=None, insufficient_data_actions=None,
                            ok_actions=None)   
        
        self.assertRaises(BotoServerError, self.synaps.put_metric_alarm, alarm) 

    
    @attr(type=['gate', 'negative'])
    def test_put_alarm_with_long_period(self):
        alarm_name = self.generate_random_name("TestAlarm_")
        metric_name = self.generate_random_name("TestMetric_")
        kw = dict(name=alarm_name, metric=metric_name,
                  namespace=self.namespace, threshold=50.0, comparison=">",
                  unit="Percent")
        
        # period: a day + one second, evaluation_periods: 1 time
        long_period_kw = kw.copy()
        long_period_kw.update(period=60 * 60 * 24 + 1,
                              evaluation_periods=1)

        self.assertRaises(BotoServerError, self.synaps.put_metric_alarm,
                          MetricAlarm(**long_period_kw))
        
        # period: a minutes, evaluation_periods: 24 * 60 + 1 times
        long_evaluation_period_kw = kw.copy()
        long_evaluation_period_kw.update(period=60,
                                         evaluation_periods=24 * 60 + 1)
        
        self.assertRaises(BotoServerError, self.synaps.put_metric_alarm,
                          MetricAlarm(**long_evaluation_period_kw))
        
        # period: an hour, evaluation_periods: 25 times (over a day)
        long_evaluation_kw = kw.copy()
        long_evaluation_kw.update(period=60 * 60,
                                  evaluation_periods=25)
        
        self.assertRaises(BotoServerError, self.synaps.put_metric_alarm,
                          MetricAlarm(**long_evaluation_kw))

    
    @attr(type=['gate'])
    def test_delete_ten_alarms(self):
        # put 10 alarms and delete all of them
        alarmnames = [self.generate_random_name("AlarmsToBeDeleted") 
                      for i in range(10)]
        
        for name in alarmnames:
            alarm = MetricAlarm(name=name, metric=self.metric_name,
                                namespace=self.namespace, statistic="Average",
                                comparison="<", threshold=2.0, period=300,
                                evaluation_periods=2, unit="Percent",
                                description=None, dimensions=self.dimensions,
                                alarm_actions=None,
                                insufficient_data_actions=None,
                                ok_actions=None)
            self.synaps.put_metric_alarm(alarm)

        time.sleep(ASYNC_WAIT)
        
        for alarm in alarmnames:
            self.synaps.delete_alarms(alarms=[alarm])
        
        time.sleep(ASYNC_WAIT)
        
        alarms = self.synaps.describe_alarms()
        for a in alarms:
            self.assertFalse(a.name in alarmnames)


    @attr(type=['negative', 'gate'])
    def test_delete_not_exist_alarm(self):
        # delete non-existing alarm
        kwargs = {'alarms': ['never_exist_alarmname']}
        self.assertRaises(BotoServerError, self.synaps.delete_alarms, **kwargs)
    
    
    @attr(type=['gate'])
    def test_describe_alarms_with_max_records(self):
        # put 10 alarms 
        prefix = "AlarmsToBeDescribed"
        alarmnames = [self.generate_random_name(prefix) for i in range(10)]
        metric_name = self.generate_random_name("metricname-")
                
        for alarmname in alarmnames:
            alarm = MetricAlarm(name=alarmname,
                metric=metric_name, namespace=self.namespace,
                statistic="Average", comparison="<", threshold=2.0,
                period=300, evaluation_periods=2, unit="Percent",
                description=None, dimensions=self.dimensions,
                alarm_actions=None, insufficient_data_actions=None,
                ok_actions=None)
            self.synaps.put_metric_alarm(alarm)
                
        alarms = self.synaps.describe_alarms(max_records=3)
        self.assertEqual(len(alarms), 3)

        alarms = self.synaps.describe_alarms(max_records=9,
                            alarm_name_prefix=prefix)
        self.assertTrue(len(alarms) <= 9)
        for a in alarms:
            self.assertTrue(a.name.startswith(prefix))

        alarms = self.synaps.describe_alarms(alarm_names=alarmnames)
        for a in alarms:
            self.assertTrue(a.name in alarmnames)
            
        self.synaps.delete_alarms(alarms=alarmnames)        
        

    @attr(type=['gate'])            
    def test_put_alarm(self):
        alarmname = self.generate_random_name("AlarmToBeDeleted")
        
        alarm_actions = ['+82 1012345678', 'test@email.abc']
        ok_actions = ['+82 1012345678', '+82 1012345678',
                      'tdsadasdest@email.abc']
        insufficient_data_actions = ['+82 1087654322', 'test@email.abc',
                                     'test@email.abc']
        alarm = MetricAlarm(name=alarmname, metric=self.metric_name,
                            namespace=self.namespace, statistic="Average",
                            comparison=">", threshold=50.0, period=300,
                            evaluation_periods=2, unit="Percent",
                            description=None, dimensions=self.dimensions,
                            alarm_actions=alarm_actions,
                            insufficient_data_actions=insufficient_data_actions,
                            ok_actions=ok_actions)
        self.synaps.put_metric_alarm(alarm)
        
        n = 20
        minute = datetime.timedelta(seconds=60)
        start = datetime.datetime.utcnow() - n * minute 
        for i in range(n):
            ret = self.synaps.put_metric_data(
                namespace=self.namespace, name=self.metric_name,
                value=i * 5.0, unit="Percent", dimensions=self.dimensions,
                timestamp=start + i * minute,
            )
        
        time.sleep(ASYNC_WAIT)
        
        alarms = self.synaps.describe_alarms(alarm_names=[alarmname])
        for a in alarms:
            self.assertSetEqual(set(ok_actions), set(a.ok_actions))
            self.assertSetEqual(set(alarm_actions), set(a.alarm_actions))
            self.assertSetEqual(set(insufficient_data_actions),
                                set(a.insufficient_data_actions))
            last_updated = datetime.datetime.strptime(a.last_updated, 
                                                      "%Y-%m-%dT%H:%M:%S.%fZ")
            self.assertTrue(datetime.datetime.utcnow() - last_updated < 
                            datetime.timedelta(seconds=60))
            
        self.synaps.delete_alarms([alarmname])


    @attr(type=['gate', 'negative'])
    def test_put_alarm_with_invalid_unit(self):
        # test check Parameters...
        alarm = MetricAlarm(name="CPU_Alarm", metric=self.metric_name,
                            namespace=self.namespace, statistic="Average",
                            comparison=">", threshold=50.0, period=300,
                            evaluation_periods=2,
                            unit="It will occur an error",
                            description=None, dimensions=self.dimensions,
                            alarm_actions=None, insufficient_data_actions=None,
                            ok_actions=None)   
        
        self.assertRaises(BotoServerError, self.synaps.put_metric_alarm, alarm)


    @attr(type=['gate'])
    def test_put_alarm_with_period(self):
        alarmname = self.generate_random_name("Test_Alarm_Period")
        alarm = MetricAlarm(name=alarmname, metric=self.metric_name,
                            namespace=self.namespace, statistic="Average",
                            comparison=">", threshold=50.0, period=6000,
                            evaluation_periods=2, unit="Percent",
                            description=None, dimensions=self.dimensions,
                            alarm_actions=None, insufficient_data_actions=None,
                            ok_actions=None)
        
        self.synaps.put_metric_alarm(alarm)
        
        td = timedelta(days=20, seconds=1) 
        
        ret1 = self.synaps.put_metric_data(
            namespace=self.namespace, name=self.metric_name,
            value=10, unit="Percent", dimensions=self.dimensions,
            timestamp=datetime.datetime.utcnow() - td
        )
         
        td2 = timedelta(seconds=7200) 
    
        ret2 = self.synaps.put_metric_data(
            namespace=self.namespace, name=self.metric_name,
            value=20, unit="Percent", dimensions=self.dimensions,
            timestamp=datetime.datetime.utcnow() - td2
        )
        
        self.assertTrue(ret2)
             
        td3 = timedelta(seconds=5400) 
        
        ret3 = self.synaps.put_metric_data(
            namespace=self.namespace, name=self.metric_name,
        value=30, unit="Percent", dimensions=self.dimensions,
            timestamp=datetime.datetime.utcnow() - td3
        )
       
        self.assertTrue(ret3)
        
        self.synaps.delete_alarms(alarms=[alarmname])
        
        td4 = timedelta(seconds=2000)  
        
        ret4 = self.synaps.put_metric_data(
            namespace=self.namespace, name=self.metric_name,
            value=40, unit="Percent", dimensions=self.dimensions,
            timestamp=datetime.datetime.utcnow() - td4
        )
        
        self.assertTrue(ret4)
      

    @attr(type=['gate'])    
    def test_describe_alarms_for_metric(self):
        prefix = "AlarmsToBeDescribed"
        alarmnames = [self.generate_random_name(prefix) for i in range(10)]
                
        for alarmname in alarmnames:
            alarm = MetricAlarm(name=alarmname,
                metric=self.metric_name, namespace=self.namespace,
                statistic="Average", comparison="<", threshold=2.0,
                period=300, evaluation_periods=2, unit="Percent",
                description=None, dimensions=self.dimensions,
                alarm_actions=None, insufficient_data_actions=None,
                ok_actions=None)
            self.synaps.put_metric_alarm(alarm)

        self.synaps.describe_alarms_for_metric(namespace=self.namespace,
            metric_name=self.metric_name, dimensions=self.dimensions)
        
        self.synaps.delete_alarms(alarmnames)


    @attr(type=['gate'])
    def test_set_alarm_state(self):
        alarmname = self.generate_random_name("TEST_ALARM_")
        
        alarm = MetricAlarm(name=alarmname,
            metric=self.metric_name, namespace=self.namespace,
            statistic="Average", comparison="<", threshold=2.0,
            period=60, evaluation_periods=1, unit="Percent",
            description=None, dimensions=self.dimensions,
            alarm_actions=None, insufficient_data_actions=None,
            ok_actions=None)
        self.synaps.put_metric_alarm(alarm)        

        time.sleep(ASYNC_WAIT)
        
        self.synaps.set_alarm_state(alarmname, state_reason="Manual input",
                                    state_value="ALARM")

        time.sleep(ASYNC_WAIT)
        self.synaps.delete_alarms(alarms=[alarmname])
        

    @attr(type=['gate', 'negative'])
    def test_put_alarm_with_utf8_name(self):
        prefix = u"TEST_\uc54c\ub78c_02"
        alarm_names = map(self.generate_random_name, [prefix])
        for alarmname in alarm_names:
            alarm = MetricAlarm(name=alarmname,
                metric=self.metric_name, namespace=self.namespace,
                statistic="Average", comparison="<", threshold=2.0,
                period=300, evaluation_periods=2, unit="Percent",
                description=None, dimensions=self.dimensions,
                alarm_actions=None, insufficient_data_actions=None,
                ok_actions=None)
            self.assertRaises(BotoServerError, self.synaps.put_metric_alarm,
                              alarm)

        
class AlarmHistoryTest(SynapsTestCase):
    @attr(type=['gate'])        
    def test_describe_alarm_history(self):
        history_list = self.synaps.describe_alarm_history(
            history_item_type="StateUpdate"
        )
        
        for history in history_list:
            self.assertTrue(history.tem_type, "StateUpdate")

class StatisticsDataTest(SynapsTestCase):
    @attr(type=['gate'])
    def test_samplecount(self):
        now = datetime.datetime.utcnow()
        now_idx = now.replace(second=0, microsecond=0)
        start_time = now - datetime.timedelta(seconds=300)
        end_time = now_idx

        # Input metric
        ret = self.synaps.put_metric_data(
            namespace=self.namespace, name="SampleCountTest",
            value=1000, unit="Bytes", dimensions=self.dimensions,
            timestamp=now_idx,
        )

        time.sleep(ASYNC_WAIT)
        
        # input metric      
        ret = self.synaps.put_metric_data(
            namespace=self.namespace, name="SampleCountTest",
            value=2000, unit="Bytes", dimensions=self.dimensions,
            timestamp=now_idx,
        )

        time.sleep(ASYNC_WAIT)

        stata = self.synaps.get_metric_statistics(
            period=300, start_time=start_time, end_time=end_time,
            metric_name="SampleCountTest", namespace=self.namespace,
            statistics=['Sum', 'Average', 'SampleCount'],
            unit="Kilobytes",
            dimensions=self.dimensions,
        )

        statb = self.synaps.get_metric_statistics(
            period=300, start_time=start_time, end_time=end_time,
            metric_name="SampleCountTest", namespace=self.namespace,
            statistics=['Sum', 'Average', 'SampleCount'],
            unit="Bytes",
            dimensions=self.dimensions,
        )

        stat1 = filter(lambda x: x.get('Timestamp') == now_idx, stata)[0]
        stat2 = filter(lambda x: x.get('Timestamp') == now_idx, statb)[0]
        
        self.assertEqual(stat1['SampleCount'], stat2['SampleCount'])

    @attr(type=['gate'])    
    def test_get_metric_statistics(self):
        now = datetime.datetime.utcnow()
        now_idx = now.replace(second=0, microsecond=0)
        start_time = now - datetime.timedelta(minutes=30)
        end_time = now

        # input metric
        metric_name = self.generate_random_name("test_metric_")
        dimensions = {self.generate_random_name("key_"):
                      self.generate_random_name("value_")}
        
        values = [10.0, 8.0, 2 ** -32, 0, 50.3, 2 ** 16, -2 ** 16, 4,
                  1000, -3000]
        keys = [now_idx - datetime.timedelta(minutes=i) 
                for i in reversed(range(len(values)))]
        data = zip(keys, values)

        for ts, v in data:
            if v == 0: continue
            self.synaps.put_metric_data(namespace=self.namespace,
                                        name=metric_name,
                                        value=v, unit="Percent",
                                        dimensions=dimensions, timestamp=ts)

        time.sleep(ASYNC_WAIT)
        
        period = 4
        stat = self.synaps.get_metric_statistics(
            period=period * 60, start_time=keys[0], end_time=keys[-1],
            metric_name=metric_name, namespace=self.namespace,
            statistics=['Sum', 'Average', 'SampleCount'],
            dimensions=dimensions,
        )
        
        timestamps = keys[::period]

        self.assertEqual([1, 3, 4],
                         map(lambda x: x.get('SampleCount'), stat))
        self.assertEqual(timestamps,
                         map(lambda x: x.get('Timestamp'), stat))
        for e, r in zip([values[0], sum(values[1:5]) / 3,
                         sum(values[5:9]) / 4],
                        map(lambda x: x.get('Average'), stat)):
            self.assertAlmostEqual(e, r) 
        for e, r in zip([values[0], sum(values[1:5]), sum(values[5:9])],
                         map(lambda x: x.get('Sum'), stat)):
            self.assertAlmostEqual(e, r)

    @attr(type=['gate'])
    def test_get_metric_statistics_with_long_period(self):
        minute = datetime.timedelta(seconds=60)
        second = datetime.timedelta(seconds=1)
        max_query_period = FLAGS.get('max_query_period_minutes')
        max_query_datapoints = FLAGS.get('max_query_datapoints')

        now = datetime.datetime.utcnow()
        now_idx = now.replace(second=0, microsecond=0)
        start_idx = now_idx - max_query_period * minute
        max_period = ((now_idx - start_idx).total_seconds() / 
                      max_query_datapoints)
        max_period = int(max_period - max_period % 60) 

        # make metric first        
        metric_name = self.generate_random_name("test_metric_")
        for t, v in [(start_idx + minute, 100.0),
                     (now_idx - (3 * max_period) * second, 100.0),
                     (now_idx - (2 * max_period) * second, 50.0),
                     (now_idx - (2 * max_period) * second, 0.0)]:
            metric_kw = dict(namespace=self.namespace, name=metric_name,
                             value=v, timestamp=t, unit='Percent')
            self.synaps.put_metric_data(**metric_kw)

        time.sleep(ASYNC_WAIT)

        # make query which could have only two datapoints
        
        long_period_kw = dict(period=max_period, start_time=start_idx,
                              end_time=now_idx, metric_name=metric_name,
                              namespace=self.namespace,
                              statistics=['SampleCount', 'Average', 'Sum'])
        
        stat = self.synaps.get_metric_statistics(**long_period_kw)
        self.assertEqual(3, len(stat))
        self.assertEqual(2, stat[-1]['SampleCount'])
        self.assertEqual(50, stat[-1]['Sum'])
        self.assertEqual(25, stat[-1]['Average'])
        self.assertEqual(1, stat[0]['SampleCount'])
        
        
    @attr(type=['gate', 'negative'])
    def test_get_metric_statistics_with_too_long_period(self):
        minute = datetime.timedelta(seconds=60)
        max_query_period = FLAGS.get('max_query_period_minutes')
        max_query_datapoints = FLAGS.get('max_query_datapoints')

        now = datetime.datetime.utcnow()
        now_idx = now.replace(second=0, microsecond=0)
        start_idx = now_idx - max_query_period * minute

        # make metric first        
        metric_name = self.generate_random_name("test_metric_")
        metric_kw = dict(namespace=self.namespace, name=metric_name,
                         value=100.0, timestamp=start_idx + minute)
        self.synaps.put_metric_data(**metric_kw)

        time.sleep(ASYNC_WAIT)
        
        # make query which has longer period than max_query_period_minutes
        # and this will raise BotoServerError
        long_period_kw = dict(period=60, start_time=start_idx - minute,
                              end_time=now_idx, metric_name=metric_name,
                              namespace=self.namespace, statistics=['Average'])
        
        self.assertRaises(BotoServerError, self.synaps.get_metric_statistics,
                          **long_period_kw)
        
        # make queries which have more datapoints than max_query_datapoints
        # or longer period than max_query_period_minutes and this will raise 
        # BotoServerError
        for period in (1, 5, 15, 30, 60, 90, 1440):
            start_idx = now_idx - (1 + max_query_datapoints) * period * minute
        
            more_data_kw = dict(period=period * 60, start_time=start_idx,
                                end_time=now_idx, metric_name=metric_name,
                                namespace=self.namespace,
                                statistics=['Average'])
            
            self.assertRaises(BotoServerError,
                              self.synaps.get_metric_statistics,
                              **more_data_kw)


class AlarmActionsTest(SynapsTestCase):
    @attr(type=['gate'])
    def test_alarm_actions(self):
        # delete Alarm
        try:
            self.synaps.delete_alarms(alarms=['AlarmActionTest'])
            time.sleep(ASYNC_WAIT)
        except BotoServerError:
            pass
        
        # add Alarm
        alarm_actions = ['+82 1093145616', 'june.yi@samsung.com']
        ok_actions = ['+82 1012345678', '+82 1093145616',
                      'june.yi@samsung.com']
        insufficient_data_actions = ['+82 1093145616', 'june.yi@samsung.com',
                                     'test@email.abc']
        alarm = MetricAlarm(name="AlarmActionTest", metric=self.metric_name,
                            namespace=self.namespace, statistic="Sum",
                            comparison=">", threshold=50.0, period=300,
                            evaluation_periods=2, unit="Percent",
                            description=None, dimensions=self.dimensions,
                            alarm_actions=alarm_actions,
                            insufficient_data_actions=insufficient_data_actions,
                            ok_actions=ok_actions)
        self.synaps.put_metric_alarm(alarm)
        time.sleep(ASYNC_WAIT)
        
        # get MetricStatistics
        n = 10
        minute = datetime.timedelta(seconds=60)
        end_time = datetime.datetime.utcnow()
        start_time = end_time - n * minute
        stats = self.synaps.get_metric_statistics(
            period=60, start_time=start_time, end_time=end_time,
            metric_name=self.metric_name, namespace=self.namespace,
            statistics=["Sum"], dimensions=self.dimensions, unit="Percent"
        )

        for s in stats:
            self.synaps.put_metric_data(namespace=self.namespace,
                                        name=self.metric_name,
                                        value= -s["Sum"],
                                        timestamp=s['Timestamp'],
                                        unit=s["Unit"],
                                        dimensions=self.dimensions)
        
        for i in range(n):
            self.synaps.put_metric_data(namespace=self.namespace,
                                        name=self.metric_name, value=i * 10,
                                        unit="Percent",
                                        dimensions=self.dimensions,
                                        timestamp=start_time + i * minute)
        
        time.sleep(ASYNC_WAIT)
        
        # delete alarm        
        self.synaps.delete_alarms(alarms=['AlarmActionTest'])
        time.sleep(ASYNC_WAIT)

    @attr(type=['gate'])
    def test_enable_alarm_actions(self):
        alarmnames = [self.generate_random_name("TEST_ALARM_") 
                      for i in range(10)]
        metric_name = self.generate_random_name("TEST_METRIC")
        for alarmname in alarmnames:
            alarm = MetricAlarm(name=alarmname,
                metric=metric_name, namespace=self.namespace,
                statistic="Average", comparison="<", threshold=2.0 * i,
                period=300, evaluation_periods=2, unit="Percent",
                description=None, dimensions=self.dimensions,
                alarm_actions=None, insufficient_data_actions=None,
                ok_actions=None)
            self.synaps.put_metric_alarm(alarm)

        time.sleep(ASYNC_WAIT)

        self.synaps.enable_alarm_actions(alarmnames)
        time.sleep(ASYNC_WAIT)
        alarms = self.synaps.describe_alarms(alarm_names=alarmnames)
        for a in alarms:
            self.assertTrue(a.actions_enabled, 'true')

        self.synaps.disable_alarm_actions(alarmnames)
        time.sleep(ASYNC_WAIT)
        alarms = self.synaps.describe_alarms(alarm_names=alarmnames)
        for a in alarms:
            self.assertEqual(a.actions_enabled, 'false')
        
        for alarm in alarmnames:
            self.synaps.delete_alarms(alarms=[alarm])
        
        time.sleep(ASYNC_WAIT)

        alarms = self.synaps.describe_alarms(alarm_names=alarmnames)
        for a in alarms:
            self.assertFalse(a.name in alarmnames)


if __name__ == "__main__":
    unittest.main()

assert synaps.tests
