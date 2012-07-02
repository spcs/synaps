.. _delete_alarms:

DeleteAlarms
=============

설명
----
지정된 모든 알람을 지운다. 알람 이름이 하나라도 데이터베이스에 없는 경우,
어떤 알람도 지워지지 않는다.

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
     - 삭제할 알람의 이름 리스트.

       Type: String list

       길이 제한: 최소 0개 부터 100개까지의 알람.
     - No

에러
----
공통으로 발생하는 매개변수는 :ref:`common_errors` 를 참고한다.

알림:
  TBD