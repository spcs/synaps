.. _delete_alarms:

DeleteAlarms
=============

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
