# -*- coding:utf-8 -*-
# Copyright 2012 Samsung SDS

import os
import sys

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "synaps", "__init__.py")):
    sys.path.insert(0, possible_topdir)

import traceback
import storm
import json
import uuid

from synaps import flags
from synaps import log as logging
from synaps import utils
from synaps.monitor.api import MetricMonitor
from synaps.db import Cassandra
from synaps.rpc import PUT_METRIC_DATA_MSG_ID

class PutMetricBolt(storm.BasicBolt):
    def initialize(self, stormconf, context):
        self.cass = Cassandra()
        self.metrics = {}
    
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

        self.metrics[metric_key].put_metric_data(
            timestamp=timestamp, value=message['value'], unit=message['unit']
        )
        
        storm.log("write metric into database %s" % (metric_key))
        
    def process(self, tup):
        metric_key = uuid.UUID(tup.values[0])
        message = json.loads(tup.values[1])
        message_id = message.get('message_id')
        
        if message_id == PUT_METRIC_DATA_MSG_ID:
            storm.log("process put_metric_data_msg (%s)" % message)
            try:
                self.process_put_metric_data_msg(metric_key, message)
            except Exception as e:
                storm.log(traceback.format_exc(e))
        else:
            storm.log("unknown message")
            pass
            

if __name__ == "__main__":
    flags.FLAGS(sys.argv)
    utils.default_flagfile()
    logging.setup()
    PutMetricBolt().run()
