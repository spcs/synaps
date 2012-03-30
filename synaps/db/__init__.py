# Copyright 2012 Samsung SDS
# All Rights Reserved

import time
import uuid
import pycassa
from pycassa import types
import struct
import json

from synaps import flags
from synaps import log as logging
from synaps import utils

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS    

class MetricValueType(types.DoubleType):
    @staticmethod
    def pack(v, *args, **kwargs):
        return struct.pack(">d", v)
    
    @staticmethod
    def unpack(v):
        return struct.unpack(">d", v)[0]

class Cassandra(object):
    TWOWEEK = 60 * 60 * 24 * 14 # 2weeks in sec
    
    def __init__(self):
        keyspace = FLAGS.get("cassandra_keyspace", "synaps_test")
        serverlist = FLAGS.get("cassandra_server_list")
        self.archives = [60, 60 * 5, 60 * 15, 60 * 60, 60 * 360, 60 * 1440]
        
        self.pool = pycassa.ConnectionPool(keyspace, server_list=serverlist)
        
        self.cf_metric = pycassa.ColumnFamily(self.pool, 'Metric')
        self.cf_metric_archive = pycassa.ColumnFamily(self.pool,
                                                      'MetricArchive')
        self.scf_stat_archive = pycassa.ColumnFamily(self.pool,
                                                     'StatArchive')
        
    @staticmethod
    def reset():
        keyspace = FLAGS.get("cassandra_keyspace", "synaps_test")
        serverlist = FLAGS.get("cassandra_server_list")
        manager = pycassa.SystemManager(server=serverlist[0])
        # drop keyspace
        try:
            manager.drop_keyspace(keyspace)
            LOG.info(_("cassandra keyspace, %s is dropped") % keyspace)
        except:
            LOG.critical(_("failed to drop cassandra keyspace, %s") % keyspace)
    
        # initialize database scheme
        try:
            manager.create_keyspace(keyspace,
                                    strategy_options={'replication_factor':
                                                      '1'})

            manager.create_column_family(keyspace=keyspace, name='Metric')
            manager.create_index(keyspace=keyspace, column_family='Metric',
                                column='project_id',
                                value_type=types.UTF8Type())
            manager.create_index(keyspace=keyspace, column_family='Metric',
                                 column='name',
                                 value_type=types.UTF8Type())
            manager.create_index(keyspace=keyspace, column_family='Metric',
                                 column='namespace',
                                 value_type=types.UTF8Type())

            manager.create_column_family(keyspace=keyspace,
                                         name='MetricArchive',
                                         comparator_type="DateType")

            manager.create_column_family(keyspace=keyspace,
                                         name='StatArchive',
                                         super=True,
                                         comparator_type="IntegerType",
                                         subcomparator_type="DateType")

            LOG.info(_("cassandra column families are generated"))
        except Exception as ex:
            LOG.critical(_("failed to initialize: %s") % ex)        
    
    def get_metric_data(self, project_id, namespace, metric_name, dimensions,
                        start, end):

        key = self.get_metric_key(project_id, namespace, metric_name,
                                  dimensions)
        return self.cf_metric_archive.get(key, column_start=start,
                                          column_finish=end)
    
        
    def get_metric_key(self, project_id, namespace, metric_name, dimensions):
        expr_list = [
            pycassa.create_index_expression("project_id", project_id),
            pycassa.create_index_expression("name", metric_name),
            pycassa.create_index_expression("namespace", namespace)             
        ]

        index_clause = pycassa.create_index_clause(expr_list)
        
        items = self.cf_metric.get_indexed_slices(index_clause)

        for k, v in items:
            if json.loads(v['dimensions']) == dimensions: 
                return k
        return None

    def put_metric_data(self, project_id, namespace, metric_name, dimensions,
                        value, unit=None, timestamp=None):
        # convert timestamp
        timestamp = utils.str_to_timestamp(timestamp) 

        # get metric key
        key = self.get_metric_key(project_id, namespace, metric_name,
                                  dimensions)
        
        # or create metric 
        if not key:
            key = uuid.uuid1().get_bytes()
            json_dim = json.dumps(dimensions)
            columns = {'project_id': project_id, 'namespace': namespace,
                       'name': metric_name, 'dimensions': json_dim}
        
            self.cf_metric.insert(key=key, columns=columns)
        
        # and put metric
        
        metric_col = {timestamp: MetricValueType.pack(value)}
        LOG.debug("PUT metric id %s: %s" % (repr(key), metric_col))
        self.cf_metric_archive.insert(key=key, columns=metric_col)
        
        # and build statistics data
        # TODO: build statistics data
        
        return key 

    def list_metrics(self, project_id, namespace=None, metric_name=None,
                     dimensions=None, next_token=""):
        def to_dict(v):
            return {'project_id': v['project_id'],
                    'dimensions': json.loads(v['dimensions']),
                    'name': v['name'],
                    'namespace': v['namespace']}
        
        def check_dimension(item):
            if isinstance(dimensions, dict): 
                def to_set(d):
                    return set(d.items())
                    
                l_set = to_set(dimensions)
                r_set = to_set(json.loads(item['dimensions']))
                return l_set.issubset(r_set)
            return True
        
        expr_list = [pycassa.create_index_expression("project_id",
                                                     project_id), ]
        if namespace:
            expr = pycassa.create_index_expression("namespace", namespace)
            expr_list.append(expr)
            
        if metric_name:
            expr = pycassa.create_index_expression("name", metric_name)
            expr_list.append(expr)
            
        index_clause = pycassa.create_index_clause(expr_list)
        items = self.cf_metric.get_indexed_slices(index_clause)
        
        metrics = [(k, to_dict(v)) for k, v in items if check_dimension(v)]
        
        return metrics
