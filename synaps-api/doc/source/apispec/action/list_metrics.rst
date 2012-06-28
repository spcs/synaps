.. _list_metrics:

List Metrics
======================

설명
----
Returns a list of valid metrics stored for the AWS account owner. Returned 
metrics can be used with GetMetricStatistics to obtain statistical data for a 
given metric.

Note
  Up to 500 results are returned for any one call. To retrieve further results, 
  use returned NextToken values with subsequent ListMetrics operations.

Note
  If you create a metric with the :ref:`put_metric_data` action, allow up to 
  fifteen minutes for the metric to appear in calls to the ListMetrics action. 
  Statistics about the metric, however, are available sooner using 
  :ref:`get_metric_statistics` .

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
     - A list of dimensions to filter against.

       Type: :ref:`dimension_filter` list

       Length constraints: Minimum of 0 item(s) in the list. Maximum of 10 
       item(s) in the list.
     - No
   * - MetricName
     - The name of the metric to filter against.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
     - No
   * - Namespace	
     - The namespace to filter against.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
     - No
   * - NextToken
     - The token returned by a previous call to indicate that there is more 
       data available.

       Type: String
     - No       
       
Response Elements
----
The following elements come wrapped in a GetMetricStatisticsResult structure.

.. list-table:: 
   :widths: 20 40
   :header-rows: 1

   * - Name
     - Description
   * - Metrics
     - A list of metrics used to generate statistics for an AWS account.

       Type: :ref:metric` list
   * - NextToken
     - A string that marks the start of the next batch of returned results.

       Type: String
     
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
   * - InvalidParameterValue
     - Bad or out-of-range value was supplied for the input parameter.
     - 400     
     
.. toctree::
   :maxdepth: 1