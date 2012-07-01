.. _index:

액션
----

다음의 액션을 지원한다.

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
   
자료 형
-------

SPCS Synaps API 는 액션 별로 다양한 자료 형을 사용한다. 이 장에서는 각각의 
자료 형을 자세히 소개한다.

알림:
  응답으로 전달되는 각각의 요소의 순서는 보장되지 않으므로 응용 프로그램은 
  특정 순서를 가정해서는 안된다. 

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
   
공통
----
.. toctree::
   :maxdepth: 1

   common/common_query_parameters
   common/common_errors
   