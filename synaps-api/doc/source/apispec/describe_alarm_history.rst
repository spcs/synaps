.. _describe_alarm_history:

Describe Alarm History
======================

설명
----
지정된 모든 알람을 지운다. 

요청 매개변수
-------------
공통으로 요구되는 매개변수는 :ref:`common_query_parameters` 를 참고한다.

.. list-table:: 
   :widths: 15 50 10
   :header-rows: 1

   * - 이름
     - 설명
     - 필수 여부
   * - AlarmNames.member.N
     - A list of alarms to be deleted.

       Type: String list

       Length constraints: Minimum of 0 item(s) in the list. Maximum of 100 
       item(s) in the list.
     - No

   * - AlarmName	
     - The name of the alarm.
       
       Type: String
       
       Length constraints: Minimum length of 1. Maximum length of 255.
     - No
   * - EndDate	
     - The ending date to retrieve alarm history.
       
       Type: DateTime
     - No
   * - HistoryItemType	
     - The type of alarm histories to retrieve.
      
       Type: String
      
       Valid Values: ConfigurationUpdate | StateUpdate | Action
     - No
   * - MaxRecords	
     - The maximum number of alarm history records to retrieve.
      
       Type: Integer
     - No
   * - NextToken	
     - The token returned by a previous call to indicate that there is more data available.
       
       Type: String
     - No
   * - StartDate	
     - The starting date to retrieve alarm history.
       
       Type: DateTime
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
   * - ResourceNotFound
     - 지정된 자원이 존재하지 않습니다.
     - 404

.. toctree::
   :maxdepth: 1
