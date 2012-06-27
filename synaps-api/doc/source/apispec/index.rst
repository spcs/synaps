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
   
   delete_alarms
   describe_alarm_history
   describe_alarms
   describe_alarms_for_metric
   disable_alarm_actions
   enable_alarm_actions
   get_metric_statistics
   list_metrics
   put_metric_alarm
   put_metric_data
   set_alarm_state
   
Data Types
----------
.. toctree::
   :maxdepth: 1
   
   alarm_history_item_type
   datapoint_type
   describe_alarm_history_result_type
   describe_alarms_for_metric_result_type
   describe_alarms_result_type
   dimension_type
   dimension_filter_type
   get_metric_statistics_result_type
   list_metric_result_type
   metric_type
   metric_alarm_type
   metric_datum_type
   statistic_set_type
   
Common
------
.. toctree::
   :maxdepth: 1

   common_query_parameters
   common_errors
   