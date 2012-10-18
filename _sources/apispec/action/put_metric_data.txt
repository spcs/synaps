.. _put_metric_data:

PutMetricData
======================

설명
----
메트릭 데이터포인트를 SPCS Synaps로 발행한다. SPCS Synaps에 해당 메트릭이 없는
경우, 해당 메트릭을 생성한다. 
  
요청 매개변수
-------------
공통으로 요구되는 매개변수는 :ref:`common_query_parameters` 를 참고한다.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - 이름
     - 설명
     - 필수 여부
   * - MetricData.member.N
     - 메트릭을 기술하는 데이터

       자료 형: :ref:`metric_datum` 리스트
     - Yes
   * - Namespace
     - 메트릭 데이터의 namespace
     
       사용자 API로는 "SPCS/"로 시작하는 namespace 는 사용할 수 없음. 해당 
       namespace는 SPCS 제품군에 예약되어 있기 때문. Admin API를 통해서
       접근한 경우 "SPCS/" 로 시작하는 namespace를 사용할 수 있음.
         
       자료 형: String

       길이 제한: 최소 1자 ~ 최대 255자
              
       형식 제한: 숫자로만 이루어진 값 사용 불가
     - Yes
            
에러
----
공통으로 발생하는 에러는 :ref:`common_errors` 를 참고한다.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1
   
   * - 에러
     - 설명
     - HTTP Status Code
   * - InvalidParameterValue
     - 입력 파라미터의 값이 규격을 위반했음
     - 400