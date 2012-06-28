.. _metric_alarm:

MetricAlarm
======================

설명
----
The :ref:`metric_alarm` data type represents an alarm. You can use 
:ref:`put_metric_alarm to create or update an alarm.

Contents
----

.. list-table:: 
   :widths: 15 50
   :header-rows: 1
   
   * - 이름
     - 설명
   * - ActionsEnabled
     - Indicates whether actions should be executed during any changes to the 
       alarm's state.

       Type: Boolean
   * - AlarmActions
     - The list of actions to execute when this alarm transitions into an ALARM 
       state from any other state. Each action is specified as an Amazon 
       Resource Number (ARN). Currently the only actions supported are 
       publishing to an Amazon SNS topic and triggering an Auto Scaling policy.

       Type: String list

       Length constraints: Minimum of 0 item(s) in the list. Maximum of 5 
       item(s) in the list.
   * - AlarmArn
     - The Amazon Resource Name (ARN) of the alarm.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 1600.
   * - AlarmConfigurationUpdatedTimestamp
     - The time stamp of the last update to the alarm configuration.

       Type: DateTime
   * - AlarmDescription
     - The description for the alarm.

       Type: String

       Length constraints: Minimum length of 0. Maximum length of 255.
   * - AlarmName
     - The name of the alarm.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
   * - ComparisonOperator
     - The arithmetic operation to use when comparing the specified Statistic 
       and Threshold. The specified Statistic value is used as the first 
       operand.

       Type: String

       Valid Values: GreaterThanOrEqualToThreshold | GreaterThanThreshold |
       LessThanThreshold | LessThanOrEqualToThreshold
   * - Dimensions
     - The list of dimensions associated with the alarm's associated metric.

       Type: :ref:`dimension` list

       Length constraints: Minimum of 0 item(s) in the list. Maximum of 10 
       item(s) in the list.
   * - EvaluationPeriods
     - The number of periods over which data is compared to the specified 
       threshold.

       Type: Integer
   * - InsufficientDataActions
     - The list of actions to execute when this alarm transitions into an 
       INSUFFICIENT_DATA state from any other state. Each action is specified as 
       an Amazon Resource Number (ARN). Currently the only actions supported are 
       publishing to an Amazon SNS topic or triggering an Auto Scaling policy.
       
       Important
         The current WSDL lists this attribute as UnknownActions.
       
       Type: String list

       Length constraints: Minimum of 0 item(s) in the list. Maximum of 5 
       item(s) in the list.
   * - MetricName
     - The name of the alarm's metric.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
   * - Namespace
     - The namespace of alarm's associated metric.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
   * - OKActions
     - The list of actions to execute when this alarm transitions into an OK 
       state from any other state. Each action is specified as an Amazon 
       Resource Number (ARN). Currently the only actions supported are 
       publishing to an Amazon SNS topic and triggering an Auto Scaling policy.

       Type: String list

       Length constraints: Minimum of 0 item(s) in the list. Maximum of 5 
       item(s) in the list.
   * - Period
     - The period in seconds over which the statistic is applied.

       Type: Integer
   * - StateReason
     - A human-readable explanation for the alarm's state.

       Type: String

       Length constraints: Minimum length of 0. Maximum length of 1023.
   * - StateReasonData
     - An explanation for the alarm's state in machine-readable JSON format

       Type: String

       Length constraints: Minimum length of 0. Maximum length of 4000.
   * - StateUpdatedTimestamp
     - The time stamp of the last update to the alarm's state.

       Type: DateTime
   * - StateValue
     - The state value for the alarm.

       Type: String

       Valid Values: OK | ALARM | INSUFFICIENT_DATA
   * - Statistic
     - The statistic to apply to the alarm's associated metric.

       Type: String

       Valid Values: SampleCount | Average | Sum | Minimum | Maximum
   * - Threshold
     - The value against which the specified statistic is compared.

       Type: Double
   * - Unit
     - The unit of the alarm's associated metric.

       Type: String

       Valid Values: Seconds | Microseconds | Milliseconds | Bytes | Kilobytes | 
       Megabytes | Gigabytes | Terabytes | Bits | Kilobits | Megabits | 
       Gigabits | Terabits | Percent | Count | Bytes/Second | Kilobytes/Second | 
       Megabytes/Second | Gigabytes/Second | Terabytes/Second | Bits/Second | 
       Kilobits/Second | Megabits/Second | Gigabits/Second | Terabits/Second | 
       Count/Second | None

       Type: String

       
.. toctree::
   :maxdepth: 1 
   