.. _index:

Synaps API Specification
========================

Welcome
-------
This is the SPCS Synaps API Reference. This guide provides detailed information 
about SPCS Synaps actions, data types, parameters, and errors.

SPCS Synaps is a web service that enables you to publish, monitor, and manage 
various metrics, as well as configure alarm actions based on data from metrics. 

Actions
-------
.. toctree::
   :maxdepth: 1
   
   action/delete_alarms
   action/describe_alarm_history
   action/describe_alarms
   action/describe_alarms_for_metric
   action/disable_alarm_actions
   action/enable_alarm_actions
   action/get_metric_statistics
   action/list_metrics
   action/put_metric_alarm
   action/put_metric_data
   action/set_alarm_state
   
Data Types
----------
.. toctree::
   :maxdepth: 1
   
   datatype/alarm_history_item
   datatype/datapoint
   datatype/describe_alarm_history_result
   datatype/describe_alarms_for_metric_result
   datatype/describe_alarms_result
   datatype/dimension
   datatype/dimension_filter
   datatype/get_metric_statistics_result
   datatype/list_metric_result
   datatype/metric
   datatype/metric_alarm
   datatype/metric_datum
   datatype/statistic_set
   
Common
------
.. toctree::
   :maxdepth: 1

   common/common_query_parameters
   common/common_errors
   