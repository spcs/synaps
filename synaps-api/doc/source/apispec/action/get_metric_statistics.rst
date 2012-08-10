.. _get_metric_statistics:

GetMetricStatistics
===================

설명
----
특정 메트릭의 통계자료를 조회한다.

SPCS Synaps는 `Period` 에서 입력한 길이 만큼의 데이터 포인트를 모아서 통계
자료를 반환한다. 예를들어, `Period` 를 1분으로 입력하고 특정 분에 맞아 떨어지는 
타임스탬프의 데이터 포인트를 30개 입력한 경우 조회 시에는 하나의 데이터 
포인트로 합쳐진 결과를 얻게 된다.

최대 2주의 통계자료를 조회할 수 있으며 한 번의 API 호출로 최대 20,160 개의 
데이터 포인트를 조회할 수 있다. 20,160 개의 데이터 포인트는 1분 단위 통계자료
14일치에 해당한다.


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
     - 메트릭과 관련된 Dimension 리스트

       자료 형: :ref:`dimension` list

       길이 제한: 최소 0개부터 최대 10개의 아이템
     - No
   * - EndTime	
     - 데이터포인트가 반환될 시간의 끝

       자료 형: DateTime
     - Yes
   * - MetricName
     - 메트릭 이름

       자료 형: String

       길이 제한: 최소 1자 ~ 최대 255자
     - Yes
   * - Namespace	
     - 메트릭의 namespace

       자료 형: String

       길이 제한: 최소 1자 ~ 최대 255자
     - Yes
   * - Period
     - 데이터포인트의 통계에 적용할 기간. 최소 60초이며 반드시 60초의 배수이어
       야 한다. 기본 값은 60이다.

       자료 형: Integer
     - Yes
   * - StartTime
     - 데이터포인트가 반환될 시간의 시작

       자료 형: DateTime
     - Yes
   * - Statistics.member.N
     - 반환될 메트릭 통계. 

       유효 값: Average | Sum | SampleCount | Maximum | Minimum

       자료 형: String list

       길이 제한: 최소 1개 ~ 5개의 아이템 
     - Yes
   * - Unit
     - 메트릭에 적용될 단위

       자료 형: String

       유효 값: Seconds | Microseconds | Milliseconds | Bytes | Kilobytes | 
       Megabytes | Gigabytes | Terabytes | Bits | Kilobits | Megabits | 
       Gigabits | Terabits | Percent | Count | Bytes/Second | Kilobytes/Second | 
       Megabytes/Second | Gigabytes/Second | Terabytes/Second | Bits/Second | 
       Kilobits/Second | Megabits/Second | Gigabits/Second | Terabits/Second | 
       Count/Second | None
     - Yes
       
       
응답
----
아래 엘리먼트가 GetMetricStatisticsResult 에 구조화되어 반환된다.

.. list-table:: 
   :widths: 20 40
   :header-rows: 1

   * - 이름
     - 설명
   * - Datapoints
     - 해당 메트릭의 데이터포인트

       자료 형: :ref:`datapoint` 리스트
     
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
