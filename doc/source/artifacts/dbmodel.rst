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
	  and comparator = 'AsciiType'
	  and default_validation_class = 'BytesType'
	  and key_validation_class = 'LexicalUUIDType'
	  and read_repair_chance = 1.0
	  and dclocal_read_repair_chance = 0.0
	  and gc_grace = 864000
	  and min_compaction_threshold = 4
	  and max_compaction_threshold = 32
	  and replicate_on_write = true
	  and compaction_strategy = 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy'
	  and caching = 'KEYS_ONLY'
	  and column_metadata = [
	    {column_name : 'history_summary',
	    validation_class : UTF8Type},
	    {column_name : 'alarm_name',
	    validation_class : UTF8Type,
	    index_name : 'AlarmHistory_alarm_name_idx',
	    index_type : 0},
	    {column_name : 'timestamp',
	    validation_class : DateType,
	    index_name : 'AlarmHistory_timestamp_idx',
	    index_type : 0},
	    {column_name : 'history_data',
	    validation_class : UTF8Type},
	    {column_name : 'history_item_type',
	    validation_class : UTF8Type,
	    index_name : 'AlarmHistory_history_item_type_idx',
	    index_type : 0},
	    {column_name : 'alarm_key',
	    validation_class : LexicalUUIDType,
	    index_name : 'AlarmHistory_alarm_key_idx',
	    index_type : 0},
	    {column_name : 'project_id',
	    validation_class : UTF8Type,
	    index_name : 'AlarmHistory_project_id_idx',
	    index_type : 0}]
	  and compression_options = {'sstable_compression' : 'org.apache.cassandra.io.compress.SnappyCompressor'};

   
Metric
,,,,,,

This column failmiy represents Metric.

.. code-block:: bash

	create column family Metric
	  with column_type = 'Standard'
	  and comparator = 'AsciiType'
	  and default_validation_class = 'BytesType'
	  and key_validation_class = 'LexicalUUIDType'
	  and read_repair_chance = 1.0
	  and dclocal_read_repair_chance = 0.0
	  and gc_grace = 864000
	  and min_compaction_threshold = 4
	  and max_compaction_threshold = 32
	  and replicate_on_write = true
	  and compaction_strategy = 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy'
	  and caching = 'KEYS_ONLY'
	  and column_metadata = [
	    {column_name : 'updated_timestamp',
	    validation_class : DateType,
	    index_name : 'Metric_updated_timestamp_idx',
	    index_type : 0},
	    {column_name : 'unit',
	    validation_class : UTF8Type},
	    {column_name : 'namespace',
	    validation_class : UTF8Type,
	    index_name : 'Metric_namespace_idx',
	    index_type : 0},
	    {column_name : 'dimensions',
	    validation_class : UTF8Type,
	    index_name : 'Metric_dimensions_idx',
	    index_type : 0},
	    {column_name : 'created_timestamp',
	    validation_class : DateType,
	    index_name : 'Metric_created_timestamp_idx',
	    index_type : 0},
	    {column_name : 'name',
	    validation_class : UTF8Type,
	    index_name : 'Metric_name_idx',
	    index_type : 0},
	    {column_name : 'project_id',
	    validation_class : UTF8Type,
	    index_name : 'Metric_project_id_idx',
	    index_type : 0}]
	  and compression_options = {'sstable_compression' : 'org.apache.cassandra.io.compress.SnappyCompressor'};

   
MetricAlarm
,,,,,,,,,,,

This column failmiy represents Metric.

.. code-block:: bash

	create column family MetricAlarm
	  with column_type = 'Standard'
	  and comparator = 'AsciiType'
	  and default_validation_class = 'BytesType'
	  and key_validation_class = 'LexicalUUIDType'
	  and read_repair_chance = 1.0
	  and dclocal_read_repair_chance = 0.0
	  and gc_grace = 864000
	  and min_compaction_threshold = 4
	  and max_compaction_threshold = 32
	  and replicate_on_write = true
	  and compaction_strategy = 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy'
	  and caching = 'KEYS_ONLY'
	  and column_metadata = [
	    {column_name : 'unit',
	    validation_class : UTF8Type},
	    {column_name : 'state_updated_timestamp',
	    validation_class : DateType,
	    index_name : 'MetricAlarm_state_updated_timestamp_idx',
	    index_type : 0},
	    {column_name : 'threshold',
	    validation_class : DoubleType},
	    {column_name : 'period',
	    validation_class : IntegerType,
	    index_name : 'MetricAlarm_period_idx',
	    index_type : 0},
	    {column_name : 'comparison_operator',
	    validation_class : UTF8Type},
	    {column_name : 'dimensions',
	    validation_class : UTF8Type},
	    {column_name : 'evaluation_periods',
	    validation_class : IntegerType},
	    {column_name : 'alarm_actions',
	    validation_class : UTF8Type},
	    {column_name : 'alarm_arn',
	    validation_class : UTF8Type},
	    {column_name : 'alarm_configuration_updated_timestamp',
	    validation_class : DateType,
	    index_name : 'MetricAlarm_alarm_configuration_updated_timestamp_idx',
	    index_type : 0},
	    {column_name : 'state_reason_data',
	    validation_class : UTF8Type},
	    {column_name : 'alarm_description',
	    validation_class : UTF8Type},
	    {column_name : 'statistic',
	    validation_class : UTF8Type,
	    index_name : 'MetricAlarm_statistic_idx',
	    index_type : 0},
	    {column_name : 'state_value',
	    validation_class : UTF8Type,
	    index_name : 'MetricAlarm_state_value_idx',
	    index_type : 0},
	    {column_name : 'alarm_name',
	    validation_class : UTF8Type,
	    index_name : 'MetricAlarm_alarm_name_idx',
	    index_type : 0},
	    {column_name : 'namespace',
	    validation_class : UTF8Type},
	    {column_name : 'state_reason',
	    validation_class : UTF8Type},
	    {column_name : 'metric_key',
	    validation_class : LexicalUUIDType,
	    index_name : 'MetricAlarm_metric_key_idx',
	    index_type : 0},
	    {column_name : 'insufficient_data_actions',
	    validation_class : UTF8Type},
	    {column_name : 'metric_name',
	    validation_class : UTF8Type},
	    {column_name : 'actions_enabled',
	    validation_class : BooleanType},
	    {column_name : 'project_id',
	    validation_class : UTF8Type,
	    index_name : 'MetricAlarm_project_id_idx',
	    index_type : 0},
	    {column_name : 'ok_actions',
	    validation_class : UTF8Type}]
	  and compression_options = {'sstable_compression' : 'org.apache.cassandra.io.compress.SnappyCompressor'};


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
	  and read_repair_chance = 1.0
	  and dclocal_read_repair_chance = 0.0
	  and gc_grace = 864000
	  and min_compaction_threshold = 4
	  and max_compaction_threshold = 32
	  and replicate_on_write = true
	  and compaction_strategy = 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy'
	  and caching = 'KEYS_ONLY'
	  and compression_options = {'sstable_compression' : 'org.apache.cassandra.io.compress.SnappyCompressor'};
