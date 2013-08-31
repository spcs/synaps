.. _metric_datum:

MetricDatum
===========

Description
-----------
Information that sent through :ref:`put_metric_data`. Used to add a new value
to existing Metric or generate new Metric.

Contents
--------

Following is contents of this data type.

.. list-table:: 
   :widths: 30 50
   :header-rows: 1
   
   * - Name
     - Description
   * - Dimensions
     - Dimensions for Metric

       Data type: :ref:`dimension` list

       Length limitation: 0 ~ 10 items
   * - MetricName
     - Metric's name.

       Data type: String

       Length limitation: 1 ~ 255 bytes
   * - StatisticValues
     - TBD - Not Yet Implemented.
   * - Timestamp
     - Timestamp for Metric. If you don't specify this parameter, Use input time
       of Metric as default. 

       Data type: DateTime
   * - Unit
     - Unit for Metric

       Data type: String

       Valid value: Seconds | Microseconds | Milliseconds | Bytes | Kilobytes | 
       Megabytes | Gigabytes | Terabytes | Bits | Kilobits | Megabits | 
       Gigabits | Terabits | Percent | Count | Bytes/Second | Kilobytes/Second | 
       Megabytes/Second | Gigabytes/Second | Terabytes/Second | Bits/Second | 
       Kilobits/Second | Megabits/Second | Gigabits/Second | Terabits/Second | 
       Count/Second | None
   * - Value
     - Value of Metric

       Data type: Double
