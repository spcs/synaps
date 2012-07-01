.. _set_alarm_state:

SetAlarmState
=============
.. DANGER::
  아직 구현되지 않은 기능 

설명
----
임시로 알람의 상태를 정한다. 상태는 지속되지 않고 다음 알람 체크 시 실제 상태로
변경된다.

요청 매개변수
-------------
공통으로 요구되는 매개변수는 :ref:`common_query_parameters` 를 참고한다.

.. list-table:: 
   :widths: 15 50 10
   :header-rows: 1

   * - 이름
     - 설명
     - 필수 여부
   * - AlarmName
     - The descriptive name for the alarm. This name must be unique within the 
       user's AWS account. The maximum length is 255 characters.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
     - Yes
   * - StateReason
     - The reason that this alarm is set to this specific state (in 
       human-readable text format)

       Type: String

       Length constraints: Minimum length of 0. Maximum length of 1023.
     - Yes
   * - StateReasonData
     - The reason that this alarm is set to this specific state (in 
       machine-readable JSON format)

       Type: String

       Length constraints: Minimum length of 0. Maximum length of 4000.
     - No
   * - StateValue
     - The value of the state.

       Type: String

       Valid Values: OK | ALARM | INSUFFICIENT_DATA
     - Yes       
     
에러
----
공통으로 발생하는 매개변수는 :ref:`common_errors` 를 참고한다.

.. list-table:: 
   :widths: 15 50 10
   :header-rows: 1

   * - 에러
     - 설명
     - HTTP Status Code
   * - InvalidFormat
     - Data was not syntactically valid JSON.
     - 400
   * - ResourceNotFound
     - The named resource does not exist.
     - 404   
