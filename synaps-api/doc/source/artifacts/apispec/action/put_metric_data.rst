.. _put_metric_data:

PutMetricData
======================

Description
----
Publish Metric Datapoint to Synaps. If there is no specified Metric, create it. 
  
Parameters
-------------

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - Name
     - Description
     - Mandatory
   * - MetricData.member.N
     - Data for describe the Metric

       Data type: :ref:`metric_datum` list
     - Yes
   * - Namespace
     - Namespace for Metric data.
       
       Because "SPCS/" is reserved for SPCS product family, namespace beginning 
       with "SPCS/" can not be used as user API. only access with Admin API can
       use namespace prefix "SPCS/".
         
       Data type: String

       Length limitation: 1 ~ 255 bytes
              
       Type limitation: Value consisting of only numbers can not be used.
     - Yes

see also :ref:`common_query_parameters` 
            
Errors
----

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1
   
   * - Error
     - Description
     - HTTP Status Code
   * - InvalidParameterValue
     - Invalid value of input parameter.
     - 400
     
see also :ref:`common_errors`      