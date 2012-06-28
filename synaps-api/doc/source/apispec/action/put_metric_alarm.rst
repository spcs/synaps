.. _put_metric_alarm:

Put Metric Alarm
======================

설명
----
Creates or updates an alarm and associates it with the specified Amazon 
CloudWatch metric. Optionally, this operation can associate one or more Amazon 
Simple Notification Service resources with the alarm.

When this operation creates an alarm, the alarm state is immediately set to 
INSUFFICIENT_DATA. The alarm is evaluated and its StateValue is set 
appropriately. Any actions associated with the StateValue is then executed.

Note
  When updating an existing alarm, its StateValue is left unchanged.
  
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
   * - ActionsEnabled
     - Indicates whether or not actions should be executed during any changes 
       to the alarm's state.

       Type: Boolean
     - No
   * - AlarmActions.member.N
     - The list of actions to execute when this alarm transitions into an ALARM 
       state from any other state. Each action is specified as an Amazon 
       Resource Number (ARN). Currently the only action supported is publishing 
       to an Amazon SNS topic or an Amazon Auto Scaling policy.

       Type: String list

       Length constraints: Minimum of 0 item(s) in the list. Maximum of 5 
       item(s) in the list.
     - No
   * - AlarmDescription	
     - The description for the alarm.

       Type: String

       Length constraints: Minimum length of 0. Maximum length of 255.
     - No
   * - AlarmName
     - The descriptive name for the alarm. This name must be unique within the 
       user's AWS account

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
     - Yes     
   * - ComparisonOperator
     - The arithmetic operation to use when comparing the specified Statistic 
       and Threshold. The specified Statistic value is used as the first operand.

       Type: String

       Valid Values: GreaterThanOrEqualToThreshold | GreaterThanThreshold | 
       LessThanThreshold | LessThanOrEqualToThreshold
     - Yes     
   * - Dimensions.member.N
     - The dimensions for the alarm's associated metric.

       Type: :ref:`dimension` list

       Length constraints: Minimum of 0 item(s) in the list. Maximum of 10 
       item(s) in the list.
     - No     
   * - EvaluationPeriods
     - The number of periods over which data is compared to the specified 
       threshold.

       Type: Integer
     - Yes     
   * - InsufficientDataActions.member.N
     - The list of actions to execute when this alarm transitions into an 
       INSUFFICIENT_DATA state from any other state. Each action is specified as 
       an Amazon Resource Number (ARN). Currently the only action supported is 
       publishing to an Amazon SNS topic or an Amazon Auto Scaling policy.

       Type: String list

       Length constraints: Minimum of 0 item(s) in the list. Maximum of 5 
       item(s) in the list.
     - No     
   * - MetricName
     - The name for the alarm's associated metric.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
     - Yes     
   * - Namespace
     - The namespace for the alarm's associated metric.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
     - Yes     
   * - OKActions.member.N
     - The list of actions to execute when this alarm transitions into an OK 
       state from any other state. Each action is specified as an Amazon 
       Resource Number (ARN). Currently the only action supported is publishing 
       to an Amazon SNS topic or an Amazon Auto Scaling policy.

       Type: String list

       Length constraints: Minimum of 0 item(s) in the list. Maximum of 5 
       item(s) in the list.
     - No   
   * - Period
     - The period in seconds over which the specified statistic is applied.

       Type: Integer
     - Yes     
   * - Statistic
     - The statistic to apply to the alarm's associated metric.

       Type: String

       Valid Values: SampleCount | Average | Sum | Minimum | Maximum
     - Yes     
   * - Threshold
     - The value against which the specified statistic is compared.

       Type: Double
     - Yes     
   * - Unit
     - The unit for the alarm's associated metric.

       Type: String

       Valid Values: Seconds | Microseconds | Milliseconds | Bytes | Kilobytes | 
       Megabytes | Gigabytes | Terabytes | Bits | Kilobits | Megabits | 
       Gigabits | Terabits | Percent | Count | Bytes/Second | Kilobytes/Second | 
       Megabytes/Second | Gigabytes/Second | Terabytes/Second | Bits/Second | 
       Kilobits/Second | Megabits/Second | Gigabits/Second | Terabits/Second | 
       Count/Second | None
     - No     
            
에러
----
공통으로 발생하는 매개변수는 :ref:`common_errors` 를 참고한다.

.. list-table:: 
   :widths: 15 50 10
   :header-rows: 1

   * - 에러
     - 설명
     - HTTP Status Code
   * - LimitExceeded
     - The quota for alarms for this customer has already been reached.
     - 400  
     
.. toctree::
   :maxdepth: 1