# -*- coding:utf-8 -*-
# Copyright 2012 Samsung SDS

import pycassa
import os
import sys
import datetime

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "synaps", "__init__.py")):
    sys.path.insert(0, possible_topdir)

import storm
import json
import uuid

from synaps import flags
from synaps import log as logging
from synaps import utils
from synaps.db import Cassandra, STAT_TYPE
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
        # TODO: pandas 라이브러리를 통해 시계열 데이터 처리 성능 개선 필요
        
        # 메트릭 가져오기
        if self.metrics.has_key(metric_key):
            data = self.metrics.get(metric_key)
        else: # 메트릭이 로드되지 않은 경우 DB 에서 로드
            loaded_data = self.cass.load_metric_data(metric_key)
            data = loaded_data.items()
            data.sort()
            self.metrics.setdefault(metric_key, data)
        
        # 메시지 값이 없는 경우 종료    
        if message['value'] is None:
            return
                
        # MetricArchive 컬럼패밀리에 데이터 입력, 볼트의 메모리에도 입력.
        timestamp = utils.parse_strtime(message['timestamp'])
        value = message.get('value')
        self.cass.insert_metric_data(metric_key, {timestamp: value})
        data.append((timestamp, value))
        data.sort()
        
        # 통계 자료 업데이트
        stat = {}
        std_time = utils.align_metrictime(timestamp)
        for resolution in self.cass.ARCHIVE:
            from_time = std_time - datetime.timedelta(seconds=resolution)
            to_time = std_time + datetime.timedelta(seconds=60)
            base_data = [v for ts, v in data if from_time <= ts < to_time]
            
            summation = sum(base_data)
            sample_count = len(base_data)
            average = summation / sample_count if sample_count != 0 else None
            minimum = min(base_data) if base_data else None
            maximum = max(base_data) if base_data else None
            
            stat[(resolution, "SUM")] = {std_time: summation}
            stat[(resolution, "SampleCount")] = {std_time: sample_count}
            stat[(resolution, "Average")] = {std_time: average}
            stat[(resolution, "Minimum")] = {std_time: minimum}
            stat[(resolution, "Maximum")] = {std_time: maximum}
            
        self.cass.insert_stat(metric_key, stat)
        storm.log("write metric into database")
        
    def process(self, tup):
        metric_key = uuid.UUID(tup.values[0])
        message = json.loads(tup.values[1])
        message_id = message.get('message_id')
        
        if message_id == PUT_METRIC_DATA_MSG_ID:
            storm.log("process put_metric_data_msg (%s)" % message)
            self.process_put_metric_data_msg(metric_key, message)
        else:
            storm.log("unknown message")
            pass
            

if __name__ == "__main__":
    flags.FLAGS(sys.argv)
    utils.default_flagfile()
    logging.setup()
    PutMetricBolt().run()
