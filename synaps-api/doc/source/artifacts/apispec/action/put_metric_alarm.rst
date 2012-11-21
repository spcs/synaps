.. _put_metric_alarm:

PutMetricAlarm
==============

Description
-----------
Create or update Alarm for Metric.

Parameters
----------

Following is list of parameters for this action.


.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - Name
     - Description
     - Mandatory
   * - ActionsEnabled
     - Whether the execution of action by changing state of the Alarm.
       Data type: Boolean
     - No
   * - AlarmActions.member.N
     - Address to send the E-mail or phone number to send SMS if the state of
       the Alarm.

       If you using international phone number, form is such as +82 10 1234 5678. 
       Country code and other phone number should be divided by space(' '). 
       only +, [0-9], space(' ') are allowed in international phone number.
       
       Refer to International Telecommunication Union ITU-T Rec. E.123 (02/2001)

       Data type: String
     - No
   * - AlarmDescription	
     - Description of Alarm.

       Data type: String

       Length limitation: 1 ~ 255 bytes
              
       Type limitation: Value consisting of only numbers can not be used.
     - No
   * - AlarmName
     - name of Alarm. It should be unique in user's all alarm. 

       Data type: String

       Length limitation: 1 ~ 255 bytes
              
       Type limitation: Value consisting of only numbers can not be used.
     - Yes
   * - ComparisonOperator
     - Operator to compare with threshold. Statistics data is used for left side
       of calculation.

       Data type: String

       Valid value: GreaterThanOrEqualToThreshold | GreaterThanThreshold | 
       LessThanThreshold | LessThanOrEqualToThreshold
     - Yes     
   * - Dimensions.member.N
     - Dimension list to be used for search.
     
       Data type: :ref:`dimension_filter` list

       Length limitation: 0 ~ 10 items
     - No
     
.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - Name
     - Description
     - Mandatory
   * - EvaluationPeriods
     - Period to compare with threshold. (minute)

       Data type: Integer
       
       Valid value: 1 ~ 100
     - Yes     
   * - InsufficientDataActions.member.N
     - Phone number to send SMS or E-mail address to send an E-mail when the
       state of alarm is Insufficient_Data. Phone number should follow the shape
       of the International phone number. 
       
       International phone number is in accordance with the form, such as
       +82 10 1234 5678. International phone code and the remaining numbers are 
       divided by space(' '). only can +, [0-9], space(' ') are available in
       this value.
              
       refer to International Telecommunication Union ITU-T Rec. E.123 (02/2001)

       Data type: String
     - No
   * - MetricName
     - Metric name for Alarm.

       Data type: String

       Length limitation: 1 ~ 255 bytes
              
       Type limitation: Value consisting of only numbers can not be used.
     - Yes
   * - Namespace	
     - Namespace for Alarm.

       Data Type: String

       Length limitation: 1 ~ 255 bytes
              
       Type limitation: Value consisting of only numbers can not be used.
     - Yes
   * - OKActions.member.N
     - Phone number to send SMS or E-mail address to send an E-mail when the
       state of alarm is Insufficient_Data. Phone number should follow the shape
       of the International phone number. 
       
       International phone number is in accordance with the form, such as
       +82 10 1234 5678. International phone code and the remaining numbers are 
       divided by space(' '). only can +, [0-9], space(' ') are available in
       this value.
              
       refer to International Telecommunication Union ITU-T Rec. E.123 (02/2001)

       Data type: String
     - No
   * - Period
     - Period to apply Statistic (sec)

       Data type: Integer
       
       Valid value : 60(1 minute) ~ 86400(24 hours), multiple of 60.
     - Yes     
   * - Statistic
     - Metric statistics for Alarm

       Data type: String

       Valid value: SampleCount | Average | Sum | Minimum | Maximum
     - Yes     
   * - Threshold
     - Threshold to be compared with statistics.

       Data type: Double
     - Yes     
   * - Unit
     - Metric's unit for Alarm.

       Data type: String

       Valid value: Seconds | Microseconds | Milliseconds | Bytes | Kilobytes | 
       Megabytes | Gigabytes | Terabytes | Bits | Kilobits | Megabits | 
       Gigabits | Terabits | Percent | Count | Bytes/Second | Kilobytes/Second | 
       Megabytes/Second | Gigabytes/Second | Terabytes/Second | Bits/Second | 
       Kilobits/Second | Megabits/Second | Gigabits/Second | Terabits/Second | 
       Count/Second | None
     - No     

see also :ref:`common_query_parameters` 
            
Errors
------

Following is list of errors for this action.

see also :ref:`common_errors` 
