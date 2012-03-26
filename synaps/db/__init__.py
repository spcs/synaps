import time
import uuid
import pycassa
from pycassa import types
import struct

from synaps import flags
from synaps import log as logging

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS    

class MetricValueType(types.DoubleType):
    @staticmethod
    def pack(v, *args, **kwargs):
        return struct.pack(">d", v)
    
    @staticmethod
    def unpack(v):
        return struct.unpack(">d", v)[0]

class MetricIdType(types.LexicalUUIDType):
    @staticmethod
    def new():
        return MetricIdType.pack(uuid.uuid4())
    
    @staticmethod
    def pack(v, *args, **kwargs):
        assert(isinstance(v, uuid.UUID))
        return v.get_bytes()
    
    @staticmethod
    def unpack(v):        
        return uuid.UUID(bytes=v)

class Cassandra(object):
    TWOWEEK = 60 * 60 * 24 * 14 # 2weeks in sec
    
    def __init__(self):
        keyspace = FLAGS.get("cassandra_keyspace", "synaps_test")
        self.pool = pycassa.ConnectionPool(keyspace)
        
        self.scf_metric = pycassa.ColumnFamily(self.pool, 'Metric')
        self.scf_metric_lookup = pycassa.ColumnFamily(self.pool,
                                                      'MetricLookup')
        self.cf_metric_archive = pycassa.ColumnFamily(self.pool,
                                                      'MetricArchive')
        
    @staticmethod
    def reset():
        keyspace = FLAGS.get("cassandra_keyspace", "synaps_test")
        manager = pycassa.SystemManager()
        # drop keyspace
        try:
            manager.drop_keyspace(keyspace)
            LOG.info(_("cassandra keyspace %s dropped") % keyspace)
        except:
            LOG.critical(_("failed to drop cassandra keyspace, %s") % keyspace)
    
        # initialize database scheme
        try:
            manager.create_keyspace(keyspace,
                                    strategy_options={'replication_factor':
                                                      '1'})
            manager.create_column_family(keyspace=keyspace,
                                         name='MetricLookup',
                                         super=True)
            manager.create_column_family(keyspace=keyspace, super=True,
                                         name='Metric')
            manager.create_column_family(keyspace=keyspace,
                                         name='MetricArchive',
                                         comparator_type="DateType")
            LOG.info(_("cassandra column families are generated"))
        except:
            LOG.critical(_("failed to initialization"))        
    
    def _serialize_dimension(self, dimensions):
        """
          {'name1': 'value1', 'name2': 'value2'}
        will be serialized to        
          name1=value1,name2=value2
        """
        items = map("=".join, sorted(dimensions.items()))
        return ",".join(items)
    
    def _build_scn(self, project_id, namespace):
        return project_id + ":" + namespace
    
    def get_metric_data(self, project_id, namespace, metric_name, dimensions,
                        start, end):

        metric_id = self._get_metric_id(project_id, namespace, metric_name,
                                        dimensions)
        return self.cf_metric_archive.get(metric_id, column_start=start,
                                          column_finish=end)
    
    def _get_metric_id(self, project_id, namespace, metric_name, dimensions):
        lookupkey = self._serialize_dimension(dimensions)
        scn = self._build_scn(project_id, namespace)
        
        metric = self.scf_metric_lookup.get(key=lookupkey,
                                            super_column=scn,
                                            columns=[metric_name, ],
                                            column_count=1)
        return metric.get(metric_name)
        

    def put_metric_data(self, project_id, namespace, metric_name, dimensions,
                        value, unit=None, timestamp=None):
        
        lookupkey = self._serialize_dimension(dimensions)
        scn = self._build_scn(project_id, namespace)
        
        try:
            metric_id = self._get_metric_id(project_id, namespace, metric_name,
                                            dimensions)
            
        except pycassa.NotFoundException:
            # create metric
            unit = unit if unit else "None"
            metric_id = MetricIdType.new()
            columns = {scn: {'dimensions': lookupkey,
                             'metric_name': metric_name,
                             'unit': unit}}
            self.scf_metric.insert(metric_id, columns)
            
            # create metric lookup index
            columns = {scn: {metric_name:metric_id}}
            self.scf_metric_lookup.insert(lookupkey, columns)
            
        # put metric data
        timestamp = timestamp if timestamp else time.time()
        
        self.cf_metric_archive.insert(metric_id,
                                      {timestamp: MetricValueType.pack(value)},
                                      ttl=self.TWOWEEK)
        
        return metric_id

    def list_metrics(self, project_id, namespace, metric_name, dimensions):
        #TODO: (june.yi) implement it
        pass
