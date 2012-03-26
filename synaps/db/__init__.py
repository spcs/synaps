import uuid
import pycassa

from synaps import flags
from synaps import log as logging

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS    

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
                                    strategy_options={'replication_factor': '1'})
            manager.create_column_family(keyspace=keyspace,
                                         name='MetricLookup',
                                         super=True)
            manager.create_column_family(keyspace=keyspace,
                                         name='Metric',
                                         comparator_type='TimeUUIDType',
                                         super=True)
            manager.create_column_family(keyspace=keyspace,
                                         name='MetricArchive',
                                         comparator_type='DateType')
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
    
    def _gen_uuid(self):
        return uuid.uuid4()

    def put_metric(self, project_id, namespace, metric_name, dimensions, value,
                   timestamp=None, unit=None):
        
        lookupkey = self._serialize_dimension(dimensions)
        scn = self._build_scn(project_id, namespace)
        
        try:
            metric_id = self.scf_metric_lookup.get(key=lookupkey,
                                                    super_column=scn,
                                                    columns=[metric_name, ],
                                                    column_count=1)
            
        except pycassa.NotFoundException:
            # create metric
            metric_id = self._gen_uuid()
            columns = {scn: {'dimensions': lookupkey,
                             'metric_name': metric_name,
                             'unit': unit}}
            LOG.info("metric_id: " + str(metric_id))
            self.scf_metric.insert(metric_id, columns)
            
            # create metric lookup index
            columns = {scn: {metric_name:metric_id}}
            self.scf_metric_lookup.insert(lookupkey, columns)
            
        # put metric data
        self.cf_metric_archive.insert(metric_id, {timestamp: value},
                                      ttl=self.TWOWEEK)
        
        return
