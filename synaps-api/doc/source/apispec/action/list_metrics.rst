.. _list_metrics:

ListMetrics
===========

설명
----
SPCS 사용자가 저장한 유효한 메트릭을 반환한다. 반환된 메트릭은
:ref:`get_metric_statistics` 에 사용해서 통계자료를 얻을 수 있다. 

알림
  최대 500 개 결과만 얻을 수 있음. 다음 리스트를 얻기 위해서는 NextToken을 사용
  해야함.


요청 매개변수
-------------
공통으로 요구되는 매개변수는 :ref:`common_query_parameters` 를 참고한다.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - 이름
     - 설명
     - 필수 여부
   * - Dimensions.member.N
     - 검색에 사용할 dimension 의 리스트

       자료 형: :ref:`dimension_filter` 리스트

       길이 제한: 최소 0개부터 최대 10개의 아이템
     - No
   * - MetricName
     - 검색에 사용할 메트릭 이름

       자료 형: String

       길이 제한: 최소 1자 ~ 최대 255자
     - No
   * - Namespace	
     - 검색에 사용할 namespace

       자료 형: String

       길이 제한: 최소 1자 ~ 최대 255자
     - No
   * - NextToken
     - 다음 데이터를 조회하기 위한 토큰.
       
       자료 형: String
     - No       
       
응답
----
아래 엘리먼트가 ListMetricsResult 에 구조화되어 반환된다.

.. list-table:: 
   :widths: 20 40
   :header-rows: 1

   * - 이름
     - 설명
   * - Metrics
     - SPCS 사용자의 메트릭 리스트

       자료 형: :ref:`metric` 리스트
   * - NextToken
     - 다음 데이터를 조회하기 위한 토큰.
       
       자료 형: String
     
에러
----
공통으로 발생하는 매개변수는 :ref:`common_errors` 를 참고한다.

알림:
  TBD