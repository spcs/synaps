.. _get_metric_statistics:

GetMetricStatistics
======================

설명
----
Gets statistics for the specified metric.

Note
  The maximum number of data points returned from a single GetMetricStatistics 
  request is 1,440. If a request is made that generates more than 1,440 data 
  points, Amazon CloudWatch returns an error. In such a case, alter the request 
  by narrowing the specified time range or increasing the specified period. 
  Alternatively, make multiple requests across adjacent time ranges.

Amazon CloudWatch aggregates data points based on the length of the period that 
you specify. For example, if you request statistics with a one-minute 
granularity, Amazon CloudWatch aggregates data points with time stamps that fall 
within the same one-minute period. In such a case, the data points queried can 
greatly outnumber the data points returned.

Note
  The maximum number of data points that can be queried is 50,850; whereas the 
  maximum number of data points returned is 1,440.

The following examples show various statistics allowed by the data point query 
maximum of 50,850 when you call GetMetricStatistics on Amazon EC2 instances 
with detailed (one-minute) monitoring enabled:

- Statistics for up to 400 instances for a span of one hour
- Statistics for up to 35 instances over a span of 24 hours
- Statistics for up to 2 instances over a span of 2 weeks

요청 매개변수
-------------
For information about the common parameters that all actions use, 
see :ref:`common_query_parameters`.

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

   * - EndTime	
     - The time stamp to use for determining the last datapoint to return. 
       The value specified is exclusive; results will include datapoints up to
       the time stamp specified.

       Type: DateTime
     - Yes
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
     - The granularity, in seconds, of the returned datapoints. Period must be 
       at least 60 seconds and must be a multiple of 60. The default value is 60.

       Type: Integer
     - Yes
   * - StartTime
     - The time stamp to use for determining the first datapoint to return. 
       The value specified is inclusive; results include datapoints with the time stamp specified.     - No

       Note
         The specified start time is rounded down to the nearest value. 
         Datapoints are returned for start times up to two weeks in the past. Specified start times that are more than two weeks in the past will not return datapoints for metrics that are older than two weeks.

       Type: DateTime
     - Yes
   * - Statistics.member.N
     - The metric statistics to return. For information about specific 
       statistics returned by GetMetricStatistics, go to :ref:`statistics` in 
       the Amazon CloudWatch Developer Guide.

       Valid Values: Average | Sum | SampleCount | Maximum | Minimum

       Type: String list

       Length constraints: Minimum of 1 item(s) in the list. Maximum of 5 
       item(s) in the list.
     - Yes
   * - Unit
     - The unit for the metric.

       Type: String

       Valid Values: Seconds | Microseconds | Milliseconds | Bytes | Kilobytes | 
       Megabytes | Gigabytes | Terabytes | Bits | Kilobits | Megabits | 
       Gigabits | Terabits | Percent | Count | Bytes/Second | Kilobytes/Second | 
       Megabytes/Second | Gigabytes/Second | Terabytes/Second | Bits/Second | 
       Kilobits/Second | Megabits/Second | Gigabits/Second | Terabits/Second | 
       Count/Second | None
     - Yes
       
       
       
       
Response Elements
----
The following elements come wrapped in a GetMetricStatisticsResult structure.

.. list-table:: 
   :widths: 20 40
   :header-rows: 1

   * - Name
     - Description
   * - Datapoints
     - The : datapoints for the specified metric.

       Type: :ref:`datapoint` list
     
에러
----
공통으로 발생하는 매개변수는 :ref:`common_errors` 를 참고한다.

.. list-table:: 
   :widths: 15 50 10
   :header-rows: 1

   * - 에러
     - 설명
     - HTTP Status Code
   * - InternalService
     - Indicates that the request processing has failed due to some unknown 
       error, exception, or failure.
     - 500
   * - InvalidParameterCombination
     - Parameters that must not be used together were used together.
     - 400
   * - InvalidParameterValue
     - Bad or out-of-range value was supplied for the input parameter.
     - 400
   * - MissingRequiredParameter
     - An input parameter that is mandatory for processing the request is not 
       supplied.
     - 400
     
     
.. toctree::
   :maxdepth: 1