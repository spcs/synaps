.. _describe_alarm_history:

DescribeAlarmHistory
======================

설명
----
특정 알람의 히스토리를 조회한다. 기간이나 아이템 타입(HistoryItemType)
에 따라 히스토리를 검색할 수 있다. 알람 이름(AlarmName)을 지정하지 않은 경우, 
사용자의 모든 알람에 해당하는 히스토리 정보가 조회된다. 

알림:
  SPCS Synaps는 알람의 삭제 여부에 관계없이 알람 히스토리를 2주간 보관한다.

요청 매개변수
-------------
공통으로 요구되는 매개변수는 :ref:`common_query_parameters` 를 참고한다.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - 이름
     - 설명
     - 필수 여부
   * - AlarmName	
     - 알람 이름
       
       자료 형: String
       
       길이 제한: 최소 1자 ~ 최대 255자
              
       형식 제한: 숫자로만 이루어진 값 사용 불가
     - No
   * - EndDate	
     - 알람 히스토리를 조회할 기간의 끝
       
       자료 형: DateTime
     - No
   * - HistoryItemType	
     - 조회할 알람 히스토리의 종류
      
       자료 형: String
      
       유효 값: ConfigurationUpdate | StateUpdate | Action
     - No
   * - MaxRecords	
     - 조회할 알람 히스토리의 최대 갯수
      
       자료 형: Integer
     - No
   * - NextToken	
     - 다음 데이터를 조회하기 위한 토큰
       
       자료 형: String
     - No
   * - StartDate	
     - 알람 히스토리를 조회할 기간의 시작
       
       자료 형: DateTime
     - No

응답
----
아래 엘리먼트가 :ref:`describe_alarm_history_result` 에 구조화되어 반환된다.

.. list-table:: 
   :widths: 30 50
   :header-rows: 1

   * - 이름
     - 설명
   * - AlarmHistoryItems
     - JSON 형식의 알람 히스토리
       
       자료 형: :ref:`alarm_history_item` 리스트
   * - NextToken
     - 다음 데이터를 조회하기 위한 토큰.
       
       자료 형: String

에러
----
공통으로 발생하는 에러는 :ref:`common_errors` 를 참고한다.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1
   
   * - 에러
     - 설명
     - HTTP Status Code
   * - InvalidNextToken
     - 주어진 next token 이 유효하지 않음
     - 400
