.. _metric_datum:

MetricDatum
======================

설명
----
The MetricDatum data type encapsulates the information sent with 
:ref:`put_metric_data` to either create a new metric or add new values to be 
aggregated into an existing metric.

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
   * - StatisticValues
     - A set of statistical values describing the metric.

       Type: :ref:`statistic_set`
   * - Timestamp
     - The time stamp used for the metric. If not specified, the default value 
       is set to the time the metric data was received.

       Type: DateTime
   * - Unit
     - The unit of the metric.

       Type: String

       Valid Values: Seconds | Microseconds | Milliseconds | Bytes | Kilobytes | 
       Megabytes | Gigabytes | Terabytes | Bits | Kilobits | Megabits | 
       Gigabits | Terabits | Percent | Count | Bytes/Second | Kilobytes/Second | 
       Megabytes/Second | Gigabytes/Second | Terabytes/Second | Bits/Second | 
       Kilobits/Second | Megabits/Second | Gigabits/Second | Terabits/Second | 
       Count/Second | None
   * - Value
     - The value for the metric.

       Important
         Although the Value parameter accepts numbers of type Double, Amazon 
         CloudWatch truncates values with very large exponents. Values with 
         base-10 exponents greater than 126 (1 x 10^126) are truncated. 
         Likewise, values with base-10 exponents less than -130 (1 x 10^-130) 
         are also truncated.
       
       Type: Double
       
.. toctree::
   :maxdepth: 1 