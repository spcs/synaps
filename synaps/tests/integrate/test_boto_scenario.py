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
import uuid
import unittest

from boto.ec2.cloudwatch.alarm import MetricAlarm

import synaps.tests
from synaps import flags
from synaps import log as logging
from synaps import utils
from synaps.tests import SynapsTestCase, attr, skip_because

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS    

ASYNC_WAIT = 3

class ScenarioCase(SynapsTestCase):
    
    @skip_because(bug=0)
    @attr(type=['gate','scenario'])    
    def test_eval_alarm(self):
        """
        Test Scenario for following sequence. 
        
        1. Put metric alarm (period 60, evaluation_periods 1)
        2. Put metric data which is over the threshold so that the alarm state 
           would be 'ALARM'
        3. Wait 2 minutes so that alarm state could be 'INSUFFICIENT_DATA'
        4. Put metric data which is under the threshold so that the alarm state
           would be 'OK'
        5. Wait 3 minutes so that alarm state could be 'INSUFFICIENT_DATA' 
        6. Describe alarm history and check if it has been changed as we are 
           expected
        
        """
        def get_state_update_value(h):
            oldstate = h.data['oldState']['stateValue']
            newstate = h.data['newState']['stateValue']
            querydate = h.data['newState']['stateReasonData']['queryDate']
            querydate = utils.parse_strtime(querydate)
            return oldstate, newstate, querydate        
        
        test_uuid = str(uuid.uuid4())
        alarmname = "TestEvalAlarm_" + test_uuid
        metricname = "TestEvalMetric_" + test_uuid
        namespace = self.namespace
        unit = "Percent"
        dimensions = {"test_id":test_uuid}
        threshold = 2.0
        
        # create metric alarm
        alarm = MetricAlarm(name=alarmname, metric=metricname,
                            namespace=namespace, statistic="Average",
                            comparison=">", threshold=threshold,
                            period=60, evaluation_periods=1, unit=unit,
                            dimensions=dimensions)
        self.synaps.put_metric_alarm(alarm)
        
        # due to put_metric_alarm is asynchronous
        time.sleep(ASYNC_WAIT)
        
        alarm_time = datetime.datetime.utcnow().replace(second=0,
                                                       microsecond=0)
        self.synaps.put_metric_data(namespace=namespace, name=metricname,
                                    value=threshold + 1, timestamp=alarm_time,
                                    unit=unit, dimensions=dimensions)

        time.sleep(60 * 5)

        ok_time = datetime.datetime.utcnow().replace(second=0,
                                                       microsecond=0)        
        self.synaps.put_metric_data(namespace=namespace, name=metricname,
                                    value=threshold - 2, timestamp=ok_time,
                                    unit=unit, dimensions=dimensions)

        time.sleep(60 * 5)
        
        histories = self.synaps.describe_alarm_history(alarm_name=alarmname,
                                            history_item_type="StateUpdate")
        histories.sort(cmp=lambda a, b: cmp(a.timestamp, b.timestamp))

        result = map(get_state_update_value, histories)
                
        expected = (('INSUFFICIENT_DATA', 'ALARM', alarm_time),
                    ('ALARM', 'INSUFFICIENT_DATA', None),
                    ('INSUFFICIENT_DATA', 'OK', ok_time),
                    ('OK', 'INSUFFICIENT_DATA', None))
        
        failmsg = "expected: %s real: %s" % (expected, result)
        
        self.assertEqual(len(result), len(expected), msg=failmsg)
        
        for ((r_new, r_old, r_time), (e_new, e_old, e_time)) in zip(result,
                                                                    expected):
            self.assertEqual(r_new, e_new, msg=failmsg)
            self.assertEqual(r_old, e_old, msg=failmsg)
            if e_time:
                self.assertTrue((r_time - e_time) < timedelta(seconds=300),
                                msg=failmsg)
        
        self.synaps.delete_alarms(alarms=[alarmname])
        
        
if __name__ == "__main__":
    unittest.main()

assert synaps.tests