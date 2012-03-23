# Copyright 2012 Samsung SDS
# All Rights Reserved

from synaps import flags
from synaps import log as logging
from synaps.db import *

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
    def put_metric_data(self, context, namespace, metric_data):
        db = DB()
        metric_by_namespace = MetricLookup(db.pool)
        project_id = context.project_id
        namespace = namespace
        
        for metric in extract_member_list(metric_data):
            dimensions = extract_member_dict(metric['dimensions'])
            metric_name = metric['metric_name']
            unit = metric['unit']
            metric_by_namespace.get_metricid_or_create(project_id, namespace,
                                                       metric_name, dimensions,
                                                       unit)
        
        # TODO:(june.yi) put_metric_data here, MAKE TESTCASE 
        import pprint
        LOG.info("context:\n" + pprint.pformat(context.to_dict()))
        LOG.info("namespace:\n" + pprint.pformat(namespace))
        LOG.info("metric_data\n" + pprint.pformat(metric_data))
        
        metrics = extract_member_list(metric_data)
        
#context:
#{'auth_token': None,
# 'is_admin': True,
# 'project_id': u'AKIAIUIUQBYNQ3G327RA',
# 'read_deleted': 'no',
# 'remote_address': '127.0.0.1',
# 'request_id': 'req-e03f36e0-5956-4114-8e32-fb7f3112c35c',
# 'roles': ['admin'],
# 'strategy': 'noauth',
# 'timestamp': '2012-03-23T06:34:40.320632',
# 'user_id': u'AKIAIUIUQBYNQ3G327RA'}
        

        
        return {}
        
