# Copyright 2012 Samsung SDS
# All Rights Reserved

import time

from synaps import flags
from synaps import log as logging
from synaps.db import Cassandra

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS    

def extract_member_list(aws_dict, key='member'):
    """
    
    ex) if key is 'member', it will convert from
    
    {'member': {'1': 'something1',
                '2': 'something2',
                '3': 'something3'}}
    
    to            
    
    ['something1', 'something2', 'something3']
    """
    
    return aws_dict[key].values()

def extract_member_dict(aws_dict, key='member'):
    """
    it will convert from
    
    {'member': {'1': {'name': {'1': u'member1'},
                      'value': {'1': u'value1'}},
                '2': {'name': {'1': u'member2'},
                      'value': {'1': u'value2'}}}}    

    to
    
    {u'member1': u'value1', u'member2': u'value2'}
    
    this is useful for processing dimension.
    """
    members = extract_member_list(aws_dict, key)
    member_list = [(member['name']['1'], member['value']['1']) 
                   for member in members]
    return dict(member_list)

class API(object):
    def __init__(self):
        self.cass = Cassandra()
    
    def put_metric_data(self, context, namespace, metric_data):
        project_id = context.project_id
        namespace = namespace
        
        for metric in extract_member_list(metric_data):
            dimensions = extract_member_dict(metric.get('dimensions'))
            metric_name = metric.get('metric_name')
            unit = metric.get('unit', None)
            value = metric.get('value')
            timestamp = metric.get('timestamp', time.time())
            self.cass.put_metric_data(project_id, namespace, metric_name,
                                      dimensions, value, unit, timestamp)
        return {}

    def list_metrics(self, context, next_token=None, dimensions=None,
                     metric_name=None, namespace=None):
        project_id = context.project_id
        dimensions = extract_member_dict(dimensions) if dimensions else None
        
        metrics = self.cass.list_metrics(project_id, namespace, metric_name,
                                         dimensions, next_token)
        
        return metrics        
        
