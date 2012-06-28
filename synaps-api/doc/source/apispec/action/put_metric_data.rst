.. _put_metric_data:

PutMetricData
======================

설명
----
Publishes metric data points to Amazon CloudWatch. Amazon Cloudwatch associates 
the data points with the specified metric. If the specified metric does not 
exist, Amazon CloudWatch creates the metric.

Note
  If you create a metric with the PutMetricData action, allow up to fifteen 
  minutes for the metric to appear in calls to the :ref:`listmetrics` action.

The size of a request is limited to 8 KB for HTTP GET requests and 40 KB for 
HTTP POST requests.

Important
  Although the Value parameter accepts numbers of type Double, Amazon CloudWatch 
  truncates values with very large exponents. Values with base-10 exponents 
  greater than 126 (1 x 10^126) are truncated. Likewise, values with base-10 
  exponents less than -130 (1 x 10^-130) are also truncated.
  
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
   * - MetricData.member.N
     - A list of data describing the metric.

       Type: :ref:`metric_datum` list
     - Yes
   * - Namespace
     - The namespace for the metric data.
     
       Note
         You cannot specify a namespace that begins with "AWS/". Namespaces that 
         begin with "AWS/" are reserved for other Amazon Web Services products 
         that send metrics to Amazon CloudWatch.
         
       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
     - Yes
            
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

Examples
----

Sample Request
****

  .. code-block:: bash
  
   The following example puts data for a single metric containing one dimension:
   https://monitoring.amazonaws.com/doc/2010-08-01/
   ?Action=PutMetricData
   &Version=2010-08-01
   &Namespace=TestNamespace
   &MetricData.member.1.MetricName=buffers
   &MetricData.member.1.Unit=Bytes
   &MetricData.member.1.Value=231434333
   &MetricData.member.1.Dimensions.member.1.Name=InstanceType
   &MetricData.member.1.Dimensions.member.1.Value=m1.small
   &AUTHPARAMS


   The following example puts data for a single metric containing two dimensions:

   https://monitoring.amazonaws.com/doc/2010-08-01/
   ?Action=PutMetricData
   &Version=2010-08-01
   &Namespace=TestNamespace
   &MetricData.member.1.MetricName=buffers
   &MetricData.member.1.Unit=Bytes
   &MetricData.member.1.Value=231434333
   &MetricData.member.1.Dimensions.member.1.Name=InstanceID
   &MetricData.member.1.Dimensions.member.1.Value=i-aaba32d4
   &MetricData.member.1.Dimensions.member.2.Name=InstanceType
   &MetricData.member.1.Dimensions.member.2.Value=m1.small
   &AUTHPARAMS


   The following example puts data for two metrics, each with two dimensions:

   https://monitoring.amazonaws.com/doc/2010-08-01/
   ?Action=PutMetricData
   &Version=2010-08-01
   &Namespace=TestNamespace
   &MetricData.member.1.MetricName=buffers
   &MetricData.member.1.Unit=Bytes
   &MetricData.member.1.Value=231434333
   &MetricData.member.1.Dimensions.member.1.Name=InstanceID
   &MetricData.member.1.Dimensions.member.1.Value=i-aaba32d4
   &MetricData.member.1.Dimensions.member.2.Name=InstanceType
   &MetricData.member.1.Dimensions.member.2.Value=m1.small
   &MetricData.member.2.MetricName=latency
   &MetricData.member.2.Unit=Milliseconds
   &MetricData.member.2.Value=23
   &MetricData.member.2.Dimensions.member.1.Name=InstanceID
   &MetricData.member.2.Dimensions.member.1.Value=i-aaba32d4
   &MetricData.member.2.Dimensions.member.2.Name=InstanceType
   &MetricData.member.2.Dimensions.member.2.Value=m1.small
   &AUTHPARAMS::
		
Sample Response
****

  .. code-block:: xml
  
   <PutMetricDataResponse xmlns="http://monitoring.amazonaws.com/doc/2010-08-01/">
     <ResponseMetadata>
       <RequestId>e16fc4d3-9a04-11e0-9362-093a1cae5385</RequestId>
     </ResponseMetadata>
   </PutMetricDataResponse>  
  
.. toctree::
   :maxdepth: 1