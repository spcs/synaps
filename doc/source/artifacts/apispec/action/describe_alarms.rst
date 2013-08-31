.. _describe_alarms:

DescribeAlarms
==============

Description
-----------
Check the Alarm that has specific name. If you don't specify name, Synaps will
return all Alarms of user. You can search Alarm using name's prefix string or
state of Alarm.

Parameters
----------

Following is list of parameters for this action.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - Name
     - Description
     - Mandatory
   * - ActionPrefix
     - TBD.
     
       Prefix string of action's name.

       Type: String

       Length limitation: 1 ~ 1024 bytes.
              
       Type limitation: Value consisting of only numbers can not be used.
     - No
   * - AlarmNamePrefix
     - Prefix string of Alarm's name. If you use AlarmNAmes, this parameter will
       be ignored.

       Type: String

       Length limitation: 1 ~ 255 bytes.
              
       Type limitation: Value consisting of only numbers can not be used.
     - No
   * - AlarmNames.member.N
     - list of AlarmName to get Alarm information.

       Type: String list

       Length limitation: 0 ~ 100 names.
     - No
   * - MaxRecords
     - Max number of Alarm to bring

       Type: Integer
     - No
   * - NextToken
     - Check from the Alarm that has this Token.

       Type: String
     - No
   * - StateValue
     - State value to check.

       Type: String

       Valid value: OK | ALARM | INSUFFICIENT_DATA
     - No

see also :ref:`common_query_parameters` 
 
Response
--------

Following elements are structured in DescribeAlarmsResult and returned.

.. list-table:: 
   :widths: 20 40
   :header-rows: 1

   * - Name
     - Description
   * - MetricAlarms	
     - Information of Alarm.

       Type: MetricAlarm list
   * - NextToken
     - The last Token of Result.
            
       Type: String

see also :ref:`common_query_parameters` 
    
Errors
------

Following is list of errors for this action.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1
   
   * - Error
     - Description
     - HTTP Status Code
   * - InvalidNextToken
     - Invalid next token.
     - 400

see also :ref:`common_errors` 