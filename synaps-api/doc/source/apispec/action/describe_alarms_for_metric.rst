.. _describe_alarm_for_metric:

Describe Alarm For Metric
======================

설명
----
Retrieves all alarms for a single metric. Specify a statistic, period, or unit 
to filter the set of alarms further.

요청 매개변수
-------------
For information about the common parameters that all actions use, see
:ref:`common_query_parameters`.

.. list-table:: 
   :widths: 15 50 10
   :header-rows: 1

   * - 이름
     - 설명
     - 필수 여부
   * - Dimensions.member.N
     - The list of dimensions associated with the metric.

       Type: :ref:`dimension` list

       Length constraints: Minimum of 0 item(s) in the list. Maximum of 10
       item(s) in the list.
     - No

   * - MetricName	
     - The name of the metric.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
     - Yes
   * - Namespace
     - The namespace of the metric.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
     - Yes
   * - Period	
     - The period in seconds over which the statistic is applied.

       Type: Integer
     - No
   * - Statistic
     - The statistic for the metric.

       Type: String

       Valid Values: SampleCount | Average | Sum | Minimum | Maximum
     - No
   * - Unit	
     - The unit for the metric.

       Type: String

       Valid Values: Seconds | Microseconds | Milliseconds | Bytes | Kilobytes | 
       Megabytes | Gigabytes | Terabytes | Bits | Kilobits | Megabits | 
       Gigabits | Terabits | Percent | Count | Bytes/Second | Kilobytes/Second | 
       Megabytes/Second | Gigabytes/Second | Terabytes/Second | Bits/Second | 
       Kilobits/Second | Megabits/Second | Gigabits/Second | Terabits/Second | 
       Count/Second | None
     - No

Response Elements
----
The following elements come wrapped in a DescribeAlarmsForMetricResult 
structure.

.. list-table:: 
   :widths: 20 40
   :header-rows: 1

   * - Name
     - Description
   * - MetricAlarms
     - A list of information for each alarm with the specified metric.

       Type: :ref:`metric_alarm` list
     
.. toctree::
   :maxdepth: 1
