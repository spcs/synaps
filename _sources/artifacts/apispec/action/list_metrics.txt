.. _list_metrics:

ListMetrics
===========

Description
-----------
Return the Metric list that user has stored. You can get Statistics of 
checked Metric using :ref:`get_metric_statistics`. 

Note
  You can get result up to 500. You need to use NextToken to get next list.


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
     - Dimension list to be used for search.
     
       Data type: :ref:`dimension_filter` list

       Length limitation: 0 ~ 10 items
     - No
   * - MetricName
     - Metric name to be used for search.

       Data type: String

       Length limitation: 1 ~ 255 bytes
              
       Type limitation: Value consisting of only numbers can not be used.
     - No
   * - Namespace	
     - Namespace to be used for search.

       Data type: String

       Length limitation: 1 ~ 255 bytes
              
       Type limitation: Value consisting of only numbers can not be used.
     - No
   * - NextToken
     - Token to check next data.
       
       Data type: String
     - No       

see also :ref:`common_query_parameters` 
       
Response
--------

Following elements are structured in ListMetricsResult and returned.

.. list-table:: 
   :widths: 20 40
   :header-rows: 1

   * - Name
     - Description
   * - Metrics
     - User's Metric list 

       Data type: :ref:`metric` list
   * - NextToken
     - Token to check next data.
       
       Data type: String
     
Error
-----

Following is list of errors for this action.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1
   
   * - Error
     - Description
     - HTTP Status Code
   * - InvalidParameterValue
     - Invalid input parameter
     - 400
     
see also :ref:`common_errors`      