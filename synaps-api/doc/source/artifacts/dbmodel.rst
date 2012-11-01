..
      Copyright 2012 Samsung SDS.
      All Rights Reserved.


Database Model
==============

Synaps stores AlarmHistory, Metrics, MetricAlarm and StatArchive in the 
Cassandra database.

Following is Cassandra Database model for Synaps. The model can be set up by
synaps-syncdb command.

 .. image:: ../images/diagrams/CassandraDatabaseModel.jpg
   :width: 100%

Keyspace Description
--------------------

The concept of keyspace is a namespace for ColumnFamilies, typically one per 
application.

The keyspace and replication factor are configurable.

.. code-block:: bash

   create keyspace synaps
     with placement_strategy = 'SimpleStrategy'
     and strategy_options = {replication_factor : 2}
     and durable_writes = true;

   
ColumnFamily Description
------------------------

ColumnFamilies contain multiple columns, each of which has a name, value, and a 
timestamp, and which are referenced by row keys. SuperColumns can be thought of 
as columns that themselves have subcolumns.

Synaps has three ColumnFamilies(AlarmHistory, Metric and MetricAlarm) and one 
SuperColumnFamily(StatArchive).

AlarmHistory
,,,,,,,,,,,,

When an alarm or its status is created or updated, alarm history data will be 
added as a row.

.. code-block:: bash

   create column family AlarmHistory
     with column_type = 'Standard'
     and comparator = 'BytesType'
     and default_validation_class = 'BytesType'
     and key_validation_class = 'LexicalUUIDType'
     and rows_cached = 0.0
     and row_cache_save_period = 0
     and row_cache_keys_to_save = 2147483647
     and keys_cached = 200000.0
     and key_cache_save_period = 14400
     and read_repair_chance = 1.0
     and gc_grace = 864000
     and min_compaction_threshold = 4
     and max_compaction_threshold = 32
     and replicate_on_write = true
     and row_cache_provider = 'SerializingCacheProvider'
     and compaction_strategy = 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy'
     and column_metadata = [
       {column_name : '616c61726d5f6b6579',
       validation_class : LexicalUUIDType,
       index_name : 'AlarmHistory_616c61726d5f6b6579_idx',
       index_type : 0},
       {column_name : '616c61726d5f6e616d65',
       validation_class : UTF8Type,
       index_name : 'AlarmHistory_616c61726d5f6e616d65_idx',
       index_type : 0},
       {column_name : '686973746f72795f64617461',
       validation_class : UTF8Type},
       {column_name : '686973746f72795f6974656d5f74797065',
       validation_class : UTF8Type,
       index_name : 'AlarmHistory_686973746f72795f6974656d5f74797065_idx',
       index_type : 0},
       {column_name : '686973746f72795f73756d6d617279',
       validation_class : UTF8Type},
       {column_name : '70726f6a6563745f6964',
       validation_class : UTF8Type,
       index_name : 'AlarmHistory_70726f6a6563745f6964_idx',
       index_type : 0},
       {column_name : '74696d657374616d70',
       validation_class : DateType,
       index_name : 'AlarmHistory_74696d657374616d70_idx',
       index_type : 0}];

   
Metric
,,,,,,

This column failmiy represents Metric.

.. code-block:: bash

   create column family Metric
     with column_type = 'Standard'
     and comparator = 'BytesType'
     and default_validation_class = 'BytesType'
     and key_validation_class = 'LexicalUUIDType'
     and rows_cached = 0.0
     and row_cache_save_period = 0
     and row_cache_keys_to_save = 2147483647
     and keys_cached = 200000.0
     and key_cache_save_period = 14400
     and read_repair_chance = 1.0
     and gc_grace = 864000
     and min_compaction_threshold = 4
     and max_compaction_threshold = 32
     and replicate_on_write = true
     and row_cache_provider = 'SerializingCacheProvider'
     and compaction_strategy = 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy'
     and column_metadata = [
       {column_name : '64696d656e73696f6e73',
       validation_class : UTF8Type,
       index_name : 'Metric_64696d656e73696f6e73_idx',
       index_type : 0},
       {column_name : '6e616d65',
       validation_class : UTF8Type,
       index_name : 'Metric_6e616d65_idx',
       index_type : 0},
       {column_name : '6e616d657370616365',
       validation_class : UTF8Type,
       index_name : 'Metric_6e616d657370616365_idx',
       index_type : 0},
       {column_name : '70726f6a6563745f6964',
       validation_class : UTF8Type,
       index_name : 'Metric_70726f6a6563745f6964_idx',
       index_type : 0},
       {column_name : '756e6974',
       validation_class : UTF8Type}];
   
MetricAlarm
,,,,,,,,,,,

This column failmiy represents Metric.

.. code-block:: bash

   create column family MetricAlarm
     with column_type = 'Standard'
     and comparator = 'BytesType'
     and default_validation_class = 'BytesType'
     and key_validation_class = 'LexicalUUIDType'
     and rows_cached = 0.0
     and row_cache_save_period = 0
     and row_cache_keys_to_save = 2147483647
     and keys_cached = 200000.0
     and key_cache_save_period = 14400
     and read_repair_chance = 1.0
     and gc_grace = 864000
     and min_compaction_threshold = 4
     and max_compaction_threshold = 32
     and replicate_on_write = true
     and row_cache_provider = 'SerializingCacheProvider'
     and compaction_strategy = 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy'
     and column_metadata = [
       {column_name : '616374696f6e735f656e61626c6564',
       validation_class : BooleanType},
       {column_name : '616c61726d5f616374696f6e73',
       validation_class : UTF8Type},
       {column_name : '616c61726d5f61726e',
       validation_class : UTF8Type},
       {column_name : '616c61726d5f636f6e66696775726174696f6e5f757064617465645f74696d657374616d70',
       validation_class : DateType,
       index_name : 'MetricAlarm_616c61726d5f636f6e66696775726174696f6e5f757064617465645f74696d657374616d70_idx',
       index_type : 0},
       {column_name : '616c61726d5f6465736372697074696f6e',
       validation_class : UTF8Type},
       {column_name : '616c61726d5f6e616d65',
       validation_class : UTF8Type,
       index_name : 'MetricAlarm_616c61726d5f6e616d65_idx',
       index_type : 0},
       {column_name : '636f6d70617269736f6e5f6f70657261746f72',
       validation_class : UTF8Type},
       {column_name : '64696d656e73696f6e73',
       validation_class : UTF8Type},
       {column_name : '6576616c756174696f6e5f706572696f6473',
       validation_class : IntegerType},
       {column_name : '696e73756666696369656e745f646174615f616374696f6e73',
       validation_class : UTF8Type},
       {column_name : '6d65747269635f6b6579',
       validation_class : LexicalUUIDType,
       index_name : 'MetricAlarm_6d65747269635f6b6579_idx',
       index_type : 0},
       {column_name : '6d65747269635f6e616d65',
       validation_class : UTF8Type},
       {column_name : '6e616d657370616365',
       validation_class : UTF8Type},
       {column_name : '6f6b5f616374696f6e73',
       validation_class : UTF8Type},
       {column_name : '706572696f64',
       validation_class : IntegerType,
       index_name : 'MetricAlarm_706572696f64_idx',
       index_type : 0},
       {column_name : '70726f6a6563745f6964',
       validation_class : UTF8Type,
       index_name : 'MetricAlarm_70726f6a6563745f6964_idx',
       index_type : 0},
       {column_name : '73746174655f726561736f6e',
       validation_class : UTF8Type},
       {column_name : '73746174655f726561736f6e5f64617461',
       validation_class : UTF8Type},
       {column_name : '73746174655f757064617465645f74696d657374616d70',
       validation_class : DateType,
       index_name : 'MetricAlarm_73746174655f757064617465645f74696d657374616d70_idx',
       index_type : 0},
       {column_name : '73746174655f76616c7565',
       validation_class : UTF8Type,
       index_name : 'MetricAlarm_73746174655f76616c7565_idx',
       index_type : 0},
       {column_name : '737461746973746963',
       validation_class : UTF8Type,
       index_name : 'MetricAlarm_737461746973746963_idx',
       index_type : 0},
       {column_name : '7468726573686f6c64',
       validation_class : DoubleType},
       {column_name : '756e6974',
       validation_class : UTF8Type}];


StatArchive
,,,,,,,,,,,

This super column failmiy is for storing metric statistics. It holds 
time-series data aggregated per minute. Its super column key is AVERAGE, 
MAXIMUM, MINIMUM, SAMPLECOUNT and SUM. 

.. code-block:: bash

   create column family StatArchive
     with column_type = 'Super'
     and comparator = 'AsciiType'
     and subcomparator = 'DateType'
     and default_validation_class = 'DoubleType'
     and key_validation_class = 'LexicalUUIDType'
     and rows_cached = 0.0
     and row_cache_save_period = 0
     and row_cache_keys_to_save = 2147483647
     and keys_cached = 200000.0
     and key_cache_save_period = 14400
     and read_repair_chance = 1.0
     and gc_grace = 864000
     and min_compaction_threshold = 4
     and max_compaction_threshold = 32
     and replicate_on_write = true
     and row_cache_provider = 'SerializingCacheProvider'
     and compaction_strategy = 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy';
