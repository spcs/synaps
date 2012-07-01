.. _describe_alarms:

DescribeAlarms
======================

설명
----
특정 이름을 가진 알람을 조회한다. 이름이 지정되지 않은 경우, 사용자의 모든 알람
을 반환한다. 알람 이름의 시작 문자열이나 알람 상태를 통해 조회할 수 있다.

요청 매개변수
-------------
공통 매개변수에 대한 정보는 :ref:`common_query_parameters` 를 참고한다.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - 이름
     - 설명
     - 필수 여부
   * - ActionPrefix
     - 아직 구현되지 않았음.
     
       액션 이름 시작 문자열.

       Type: String

       길이 제한: 최소 1자, 최대 1024자.
     - No
   * - AlarmNamePrefix
     - 알람 이름의 시작 문자열. AlarmNames 매개변수를 사용한 경우 본 매개변수는
       무시한다.

       Type: String

       길이 제한: 최소 1자, 최대 255자.
     - No
   * - AlarmNames.member.N
     - 알람 정보를 얻어올 알람 이름의 리스트.

       Type: String list

       길이 제한: 최소 0개의 이름, 최대 100개의 이름.
     - No
   * - MaxRecords
     - 얻어올 알람의 최대 갯수.

       Type: Integer
     - No
   * - NextToken
     - 해당 토큰을 키로하는 알람부터 조회

       Type: String
     - No
   * - StateValue
     - 일치하는 알람의 상태값.

       Type: String

       유효 값: OK | ALARM | INSUFFICIENT_DATA
     - No
 
응답
----
다음 자료를 DescribeAlarmsResult 에 담아 반환한다.

.. list-table:: 
   :widths: 20 40
   :header-rows: 1

   * - 이름
     - 설명
   * - MetricAlarms	
       알람 정보

       Type: MetricAlarm list
   * - NextToken
     - 결과의 마지막 토큰
       
       Type: String
    
에러
----
공통으로 발생하는 매개변수는 :ref:`common_errors` 를 참고한다.

알림:
  (TBD) 반환하는 에러는 아직 모두 정의되지 않았다.

.. list-table:: 
   :widths: 15 50 10
   :header-rows: 1

   * - 에러
     - 설명
     - HTTP Status Code
   * - InvalidNextToken
     - The next token specified is invalid.
     - 400