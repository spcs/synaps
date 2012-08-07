.. _disable_alarm_actions:

DisableAlarmActions
===================

설명
----
특정 알람에 대한 액션을 비활성화한다. 알람의 액션이 비활성화된 경우 알람의 
상태가 바뀌더라도 알람 액션이 실행되지 않는다.

요청 매개변수
-------------
공통으로 요구되는 매개변수는 :ref:`common_query_parameters` 를 참고한다.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - 이름
     - 설명
     - 필수 여부
   * - AlarmNames.member.N
     - 액션을 비활성화 할 알람 이름의 리스트

       자료 형: String 리스트

       길이 제한: 최소 0개부터 최대 100개의 아이템
     - Yes
 
에러
----
공통으로 발생하는 매개변수는 :ref:`common_errors` 를 참고한다.
