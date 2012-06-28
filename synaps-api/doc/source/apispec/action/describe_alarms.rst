.. _describe_alarms:

DescribeAlarms
======================

설명
----
Retrieves alarms with the specified names. If no name is specified, all alarms 
for the user are returned. Alarms can be retrieved by using only a prefix for 
the alarm name, the alarm state, or a prefix for any action.

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
   * - ActionPrefix
     - The action name prefix.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 1024.
     - No
   * - AlarmNamePrefix
     - The alarm name prefix. AlarmNames cannot be specified if this parameter 
       is specified.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
     - No
   * - AlarmNames.member.N
     - A list of alarm names to retrieve information for.

       Type: String list

       Length constraints: Minimum of 0 item(s) in the list. Maximum of 100 
       item(s) in the list.
     - No
   * - MaxRecords
     - The maximum number of alarm descriptions to retrieve.

       Type: Integer
     - No
   * - NextToken
     - The token returned by a previous call to indicate that there is more 
       data available.

       Type: String
     - No
   * - StateValue
     - The state value to be used in matching alarms.

       Type: String

       Valid Values: OK | ALARM | INSUFFICIENT_DATA
     - No
 
Response Elements
----
The following elements come wrapped in a DescribeAlarmHistoryResult structure.

.. list-table:: 
   :widths: 20 40
   :header-rows: 1

   * - Name
     - Description
   * - AlarmHistoryItems
     - A list of alarm histories in JSON format.
       
       Type: AlarmHistoryItem list
   * - NextToken
     - A string that marks the start of the next batch of returned results.
       
       Type: String
    
에러
----
공통으로 발생하는 매개변수는 :ref:`common_errors` 를 참고한다.

.. list-table:: 
   :widths: 15 50 10
   :header-rows: 1

   * - 에러
     - 설명
     - HTTP Status Code
   * - InvalidNextToken
     - The next token specified is invalid.
     - 400