.. _datapoint:

Datapoint
=========

Description
----
Datapoint data type contains Statistic data which is calculated from Metric data.

Contents
----

.. list-table:: 
   :widths: 30 50
   :header-rows: 1
   
   * - Name
     - Description
   * - Average
     - Average of Metric value.

       Data type: Double
   * - Maximum
     - Maximum value of Metric

       Data type: Double
   * - Minimum
     - Minimum value of Metric

       Data type: Double
   * - SampleCount
     - Count of Metric samples

       Data type: Double
   * - Sum
     - Sum of Metric samples

       Data type: Double
   * - Timestamp
     - Timestamp for Datapoint

       Data type: DateTime
   * - Unit
     - Standard unit for Datapoint

       Data type: String

       Valid value: Seconds | Microseconds | Milliseconds | Bytes | Kilobytes | 
       Megabytes | Gigabytes | Terabytes | Bits | Kilobits | Megabits | 
       Gigabits | Terabits | Percent | Count | Bytes/Second | Kilobytes/Second | 
       Megabytes/Second | Gigabytes/Second | Terabytes/Second | Bits/Second | 
       Kilobits/Second | Megabits/Second | Gigabits/Second | Terabits/Second | 
       Count/Second | None
   