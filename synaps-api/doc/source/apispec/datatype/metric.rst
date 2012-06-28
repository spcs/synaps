.. _metric:

Metric
======================

설명
----
The Metric data type contains information about a specific metric. If you call 
:ref:`list_metrics`, Amazon CloudWatch returns information contained by this 
data type.

The example in the Examples section publishes two metrics named buffers and 
latency. Both metrics are in the examples namespace. Both metrics have two 
dimensions, InstanceID and InstanceType.

Contents
----

.. list-table:: 
   :widths: 15 50
   :header-rows: 1
   
   * - 이름
     - 설명
   * - Dimensions
     - A list of dimensions associated with the metric.

       Type: :ref:`dimension` list

       Length constraints: Minimum of 0 item(s) in the list. Maximum of 10 
       item(s) in the list.
   * - MetricName
     - The name of the metric.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
   * - Namespace
     - The namespace of the metric.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
       
.. toctree::
   :maxdepth: 1 