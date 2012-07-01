.. _datapoint:

Datapoint
======================

설명
----
The Datapoint data type encapsulates the statistical data that Amazon 
CloudWatch computes from metric data.

Contents
--------

.. list-table:: 
   :widths: 15 50
   :header-rows: 1
   
   * - 이름
     - 설명
   * - Average
     - The average of metric values that correspond to the datapoint.

       Type: Double
   * - Maximum
     - The maximum of the metric value used for the datapoint.

       Type: Double
   * - Minimum
     - The minimum metric value used for the datapoint.

       Type: Double
   * - SampleCount
     - The number of metric values that contributed to the aggregate value of 
       this datapoint.

       Type: Double
   * - Sum
     - The sum of metric values used for the datapoint.

       Type: Double
   * - Timestamp
     - The time stamp used for the datapoint.

       Type: DateTime
   * - Unit
     - The standard unit used for the datapoint.

       Type: String

       Valid Values: Seconds | Microseconds | Milliseconds | Bytes | Kilobytes | 
       Megabytes | Gigabytes | Terabytes | Bits | Kilobits | Megabits | 
       Gigabits | Terabits | Percent | Count | Bytes/Second | Kilobytes/Second | 
       Megabytes/Second | Gigabytes/Second | Terabytes/Second | Bits/Second | 
       Kilobits/Second | Megabits/Second | Gigabits/Second | Terabits/Second | 
       Count/Second | None
       
.. toctree::
   :maxdepth: 1 
   