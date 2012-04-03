# Copyright 2012 Samsung SDS
# All Rights Reserved

import time

from synaps import flags
from synaps import log as logging
from synaps.db import Cassandra
from synaps import utils

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS    

class API(object):
    def __init__(self):
        self.cass = Cassandra()
    
    def put_metric_data(self, context, namespace, metric_data):
        project_id = context.project_id
        namespace = namespace
        
        for metric in utils.extract_member_list(metric_data):
            dimensions = utils.extract_member_dict(metric.get('dimensions'))
            metric_name = metric.get('metric_name')
            unit = metric.get('unit', None)
            value = metric.get('value')
            timestamp = metric.get('timestamp', time.time())
            timestamp = utils.str_to_timestamp(timestamp) 
            self.cass.put_metric_data(project_id, namespace, metric_name,
                                      dimensions, value, unit, timestamp)
        return {}

    def list_metrics(self, context, next_token=None, dimensions=None,
                     metric_name=None, namespace=None):
        project_id = context.project_id
        dimensions = utils.extract_member_dict(dimensions) \
                     if dimensions else None
        metrics = self.cass.list_metrics(project_id, namespace, metric_name,
                                         dimensions, next_token)
        
        return metrics

    def get_metric_statistics(self, context):
        pass
        
