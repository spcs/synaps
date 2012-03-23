import uuid

from synaps import flags
from synaps import log as logging
import pycassa
from pycassa.cassandra.ttypes import NotFoundException

LOG = logging.getLogger(__name__)
FLAGS = flags.FLAGS    

class DB(object):
    def __init__(self):
        keyspace = FLAGS.get("cassandra_keyspace", "synaps_test")
        self.pool = pycassa.ConnectionPool(keyspace)

class CassandraObject(object):
    scf_sep = ":"
    cfname = ""
    
    def __init__(self, pool):
        self.pool = pool
        self.cf = pycassa.ColumnFamily(pool, self.cfname)

class Metric(CassandraObject):
    cfname = "Metric"
    
    pass

class MetricLookup(CassandraObject):
    cfname = "MetricLookup"
    
    def _build_key(self, dimensions):
        """
        will be converted from
          {'name1': 'value1', 'name2': 'value2'}
        to        
          name1=value1,name2=value2
        """
        items = sorted(dimensions.items())
        items = map(lambda x: "=".join(x), items)
        return ",".join(items)
    
    def _build_super_column(self, project_id, namespace, metric_name):
        return self.scf_sep.join((project_id, namespace, metric_name))
    
    def get_metricid(self, project_id, namespace, metric_name, dimensions):
        key = self._build_key(dimensions)
        super_column = self._build_super_column(project_id, namespace,
                                                metric_name)
        return self.cf.get(key=key, super_column=super_column,
                           columns=[metric_name])
    
    def create_metric(self, project_id, namespace, metric_name, dimensions):
        pass
    
    def get_metricid_or_create(self, project_id, namespace, metric_name,
                               dimensions, unit=None):
        try:
            id = self.get_metricid(project_id, namespace, metric_name,
                                   dimensions)
        except NotFoundException:
            # TODO:(june.yi)
            id = 0
        return id
