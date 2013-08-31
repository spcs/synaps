.. _user_api:

User API Specification
======================

Synaps provides AWS CloudWatch compatible API.


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

Note:
  The elements in the response are not sorted.   

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

Value limitation
------

.. toctree::
   :maxdepth: 1
   
   limitation/value_limitation