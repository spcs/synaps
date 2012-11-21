.. _describe_alarms_for_metric:

DescribeAlarmsForMetric
=======================

Description
-----------
Check all Alarm in single Metric. You can search Alarm using Statistic type,
Period or Unit.

Parameters
---------- 

Following is list of parameters for this action.


.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - Name
     - Description
     - Mandatory
   * - Dimensions.member.N
     - Dimensions list in respect of Metric.

       Data type: :ref:`dimension` list

       Length limitation: 0 ~ 10 items list.
     - No
   * - MetricName	
     - Metric name

       Data type: String

       Length limitation: 1 ~ 255 bytes
              
       Type limitation: Value consisting of only numbers can not be used.
     - Yes
   * - Namespace
     - Namespace of Metric

       Data type: String

       Length limitation: 1 ~ 255 bytes
              
       Type limitation: Value consisting of only numbers can not be used.
     - Yes
   * - Period	
     - Period to apply Statistic (sec)
     
       Data type: Integer
     - No
   * - Statistic
     - Metric statistic.

       Data type: String

       Valid value: SampleCount | Average | Sum | Minimum | Maximum
     - No
   * - Unit	
     - Unit of Metric.

       Data type: String

       Valid value: Seconds | Microseconds | Milliseconds | Bytes | Kilobytes | 
       Megabytes | Gigabytes | Terabytes | Bits | Kilobits | Megabits | 
       Gigabits | Terabits | Percent | Count | Bytes/Second | Kilobytes/Second | 
       Megabytes/Second | Gigabytes/Second | Terabytes/Second | Bits/Second | 
       Kilobits/Second | Megabits/Second | Gigabits/Second | Terabits/Second | 
       Count/Second | None
     - No

see also :ref:`common_query_parameters` 

Response
--------

Following elements are structured in DescribeAlarmsForMetricResult and returned.

.. list-table:: 
   :widths: 20 40
   :header-rows: 1

   * - Name
     - Description
   * - MetricAlarms
     - List of each Alarm's information for specific Metric.

       Data type: :ref:`metric_alarm` list
     
Errors
------

see also :ref:`common_errors` 
