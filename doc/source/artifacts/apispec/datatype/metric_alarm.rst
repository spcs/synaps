.. _metric_alarm:

MetricAlarm
===========

Description
-----------
:ref:`metric_alarm` data type shows Alarm. It can create or update Alarm
using :ref:`put_metric_alarm` action.

Contents
--------

Following is contents of this data type.

.. list-table:: 
   :widths: 30 50
   :header-rows: 1
   
   * - Name
     - Description
   * - ActionsEnabled
     - Whether the execution of action by changing state of the Alarm.
     
       Data type: Boolean
   * - AlarmActions
     - Address to send the E-mail or phone number to send SMS if the state of
       the Alarm.

       Data type: String list
   * - AlarmArn
     - Resource Number of Alarm.

       Data type: String

       Length limitation: 1 ~ 1000 bytes
   * - AlarmConfigurationUpdatedTimestamp
     - Time of the most recent alarm setting has been changed

       Data type: DateTime
   * - AlarmDescription
     - Alarm's description

       Data type: String

       Length limitation: 0 ~ 255 bytes
   * - AlarmName
     - Alarm's name

       Data type: String

       Length limitation: 1 ~ 255 bytes
   * - ComparisonOperator
     - Operator to compare with threshold. Statistics data is used for left side
       of calculation.

       Data type: String

       Valid value: GreaterThanOrEqualToThreshold | GreaterThanThreshold | 
       LessThanThreshold | LessThanOrEqualToThreshold
   * - Dimensions
     - Dimension list for Alarm's Metric.

       Data type: :ref:`dimension` list

       Length limitation: 0 ~ 10 items
   * - EvaluationPeriods
     - Number of data to compare with threshold.

       Data type: Integer
   * - InsufficientDataActions
     - List of phone number to send SMS or E-mail address to send an E-mail when the
       state of alarm is Insufficient_Data. 

       Data type: String list
   * - MetricName
     - Metric's name for Alarm.

       Data type: String

       Length limiation: 1 ~ 255 bytes
   * - Namespace
     - Metric's namespace for Alarm.

       Type: String

       Length limitation: 1 ~ 255 bytes
   * - OKActions
     - List of phone number to send SMS or E-mail address to send an E-mail when the
       state of alarm is Insufficient_Data.

       Data type: String list
   * - Period
     - Period to apply Statistic (sec)

       Data type: Integer


.. list-table:: cont' 
   :widths: 30 50
   :header-rows: 1
   
   * - Name
     - Description       
   * - StateReason
     - Reason of Alarm state. (for human)

       Data type: String

       Length limitation: 0 ~ 1023 bytes
   * - StateReasonData
     - Reason of Alarm state. (JSON-formatted)

       Data type: String

       Length limitation: 0 ~ 4000 bytes
   * - StateUpdatedTimestamp
     - Timestamp of the most recent alarm' state has been changed.

       Data type: DateTime
   * - StateValue
     - Value of state for Alarm.

       Data type: String

       Valid value: OK | ALARM | INSUFFICIENT_DATA
   * - Statistic
     - Statistic of Metric for Alarm.

       Data type: String

       Valid value: SampleCount | Average | Sum | Minimum | Maximum
   * - Threshold
     - Threshold to compare with statistics.

       Data type: Double
   * - Unit
     - Unit of Metric for Alarm.

       Data type: String

       Valid value: Seconds | Microseconds | Milliseconds | Bytes | 
       Kilobytes | Megabytes | Gigabytes | Terabytes | Bits | Kilobits | 
       Megabits | Gigabits | Terabits | Percent | Count | Bytes/Second | 
       Kilobytes/Second | Megabytes/Second | Gigabytes/Second | 
       Terabytes/Second | Bits/Second | Kilobits/Second | Megabits/Second | 
       Gigabits/Second | Terabits/Second | Count/Second | None

   