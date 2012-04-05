# Copyright 2012 Samsung SDS
# All Rights Reserved

import time
import uuid
import pycassa
import datetime
from pycassa import types
import struct
import json

from collections import OrderedDict
from synaps import flags
from synaps import log as logging
from synaps import utils

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS    

STAT_TYPE = types.CompositeType(types.IntegerType(), # statistics resolution
                                types.AsciiType()) # Average | SampleCount ... 

class Cassandra(object):
    METRIC_TTL = FLAGS.get('metric_ttl')
    STATISTICS_TTL = FLAGS.get('statistics_ttl')
    ARCHIVE = map(lambda x: int(x) * 60, FLAGS.get('statistics_archives'))
    
    def __init__(self):
        keyspace = FLAGS.get("cassandra_keyspace", "synaps_test")
        serverlist = FLAGS.get("cassandra_server_list")
        
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
        replication_factor = FLAGS.get("cassandra_replication_factor")
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
                                                      replication_factor})

            manager.create_column_family(
                keyspace=keyspace,
                name='Metric',
                key_validation_class=pycassa.LEXICAL_UUID_TYPE
            )
            manager.create_index(keyspace=keyspace, column_family='Metric',
                                column='project_id',
                                value_type=types.UTF8Type())
            manager.create_index(keyspace=keyspace, column_family='Metric',
                                 column='name',
                                 value_type=types.UTF8Type())
            manager.create_index(keyspace=keyspace, column_family='Metric',
                                 column='namespace',
                                 value_type=types.UTF8Type())

            manager.create_column_family(
                keyspace=keyspace,
                name='MetricArchive',
                key_validation_class=pycassa.LEXICAL_UUID_TYPE,
                comparator_type=pycassa.DATE_TYPE,
                default_validation_class=pycassa.DOUBLE_TYPE
            )

            manager.create_column_family(
                keyspace=keyspace,
                name='StatArchive', super=True,
                key_validation_class=pycassa.LEXICAL_UUID_TYPE,
                comparator_type=STAT_TYPE,
                subcomparator_type=pycassa.DATE_TYPE,
                default_validation_class=pycassa.DOUBLE_TYPE
            )

            LOG.info(_("cassandra column families are generated"))
        except Exception as ex:
            LOG.critical(_("failed to initialize: %s") % ex)        
    
    def _get_metric_data(self, project_id, namespace, metric_name, dimensions,
                        start, end):

        key = self._get_metric_key(project_id, namespace, metric_name,
                                  dimensions)
        return self.cf_metric_archive.get(key, column_start=start,
                                          column_finish=end)
    
        
    def _get_metric_key(self, project_id, namespace, metric_name, dimensions):
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
        def get_stat(metric_id, super_column, aligned_timestamp):
            """
            super_column: (60, 'Average')
            """
            resolution, statistic = super_column
            try:
                ret = self.scf_stat_archive.get(metric_id,
                                                super_column=super_column,
                                                columns=[aligned_timestamp])
            except pycassa.NotFoundException:
                if statistic in ("Minimum", "Maximum"):
                    ret = {aligned_timestamp: None}
                else:
                    ret = {aligned_timestamp: 0.0}
            return  ret.get(aligned_timestamp)

        def put_stats(metric_id, resolution, timestamp, value):
            stattime = utils.align_metrictime(timestamp, resolution)

            statistics = ["Sum", "SampleCount", "Average", "Minimum",
                          "Maximum"]
            super_column_names = [(resolution, s) for s in statistics]
            (p_sum, p_n_samples, p_avg, p_min, p_max) = [
                get_stat(metric_id, sc_name, stattime)
                for sc_name in super_column_names
            ]

            cur_sum = p_sum + value
            cur_n_samples = p_n_samples + 1
            cur_avg = cur_sum / cur_n_samples
            cur_min = p_min if p_min and p_min <= value else value
            cur_max = p_max if p_max and p_max >= value else value
            
            values = {
                (resolution, "Sum"): {stattime: cur_sum},
                (resolution, "SampleCount"): {stattime: cur_n_samples},
                (resolution, "Average"): {stattime: cur_avg},
                (resolution, "Minimum"): {stattime: cur_min},
                (resolution, "Maximum"): {stattime: cur_max}
            }
            
            self.scf_stat_archive.insert(metric_id, values,
                                         ttl=self.STATISTICS_TTL)
            LOG.info("statistics inserted for %s -> %s (%d) " % (str(timestamp),
                                                                 str(stattime),
                                                                 resolution))
            LOG.info(values)
        
        # get metric key
        key = self._get_metric_key(project_id, namespace, metric_name,
                                  dimensions)
        
        # or create metric 
        if not key:
            key = uuid.uuid4()
            json_dim = json.dumps(dimensions)
            columns = {'project_id': project_id, 'namespace': namespace,
                       'name': metric_name, 'dimensions': json_dim}
        
            self.cf_metric.insert(key=key, columns=columns)
        
        # if it doesn't hav a value to put, then return
        if value is None: 
            return key
        
        metric_col = {timestamp: value}
        
        for k, v in metric_col.items():
            LOG.debug("PUT metric id %s: %s %s" % (key, metric_col, str(k)))
        self.cf_metric_archive.insert(key=key, columns=metric_col,
                                      ttl=self.METRIC_TTL)
        
        # and build statistics data
        stats = map(lambda r: put_stats(key, r, timestamp, value),
                    self.ARCHIVE)
        
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
    
    def get_metric_statistics(self, project_id, namespace, metric_name,
                              start_time, end_time, period, statistics,
                              unit=None, dimensions=None):
        # get metric key
        key = self._get_metric_key(project_id, namespace, metric_name,
                                   dimensions)

        # or return {}
        if not key:
            return {}
        
        stat_dict = {}
        for statistic in statistics:
            statistic = utils.to_ascii(statistic)
            super_column = (period, statistic)
            try:
                stat = self.scf_stat_archive.get(key,
                                                 super_column=super_column,
                                                 column_start=start_time,
                                                 column_finish=end_time)
            except pycassa.NotFoundException:
                LOG.debug("not found %s %s ~ %s" % (super_column, start_time,
                                                   end_time))
                stat = {}
                
            stat_dict[statistic] = stat

        # build stat info
        return self.restructed_stats(stat_dict)
    
    def restructed_stats(self, stat):
        def get_stat(timestamp):
            ret = {}
            for key in stat.keys():
                ret[key] = stat[key][timestamp]
            return ret
        
        ret = []
        timestamps = reduce(lambda x, y: x if x == y else None,
                            map(lambda x: x.keys(), stat.values()))
        
        for timestamp in timestamps:
            ret.append((timestamp, get_stat(timestamp)))

        return ret
