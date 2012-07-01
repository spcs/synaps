.. _describe_alarms_for_metric:

DescribeAlarmsForMetric
=======================

설명
----
단일 메트릭에 대한 모든 알람을 조회한다. 통계 방법, 기간 또는 단위를 지정해서
조회할 수 있다.

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
     - 메트릭과 연관된 dimensions 리스트

       자료 형: :ref:`dimension` list

       길이 제한: 최소 0개 최대 10개의 아이템을 갖는 리스트
     - No
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
     - 통계를 적용할 기간 (초 단위)

       자료 형: Integer
     - No
   * - Statistic
     - 메트릭 통계

       자료 형: String

       유효 값: SampleCount | Average | Sum | Minimum | Maximum
     - No
   * - Unit	
     - 메트릭 단위

       자료 형: String

       유효 값: Seconds | Microseconds | Milliseconds | Bytes | Kilobytes | 
       Megabytes | Gigabytes | Terabytes | Bits | Kilobits | Megabits | 
       Gigabits | Terabits | Percent | Count | Bytes/Second | Kilobytes/Second | 
       Megabytes/Second | Gigabytes/Second | Terabytes/Second | Bits/Second | 
       Kilobits/Second | Megabits/Second | Gigabits/Second | Terabits/Second | 
       Count/Second | None
     - No

응답
----
다음 엘리먼트들이 DescribeAlarmsForMetricResult 구조에 담겨 반환된다.

.. list-table:: 
   :widths: 20 40
   :header-rows: 1

   * - 이름
     - 설명
   * - MetricAlarms
     - 특정 메트릭에 대한 각각의 알람 정보를 담은 리스트

       자료 형: :ref:`metric_alarm` 리스트
     
에러
----
공통으로 발생하는 매개변수는 :ref:`common_errors` 를 참고한다.

알림:
  (TBD) 반환하는 에러는 아직 모두 정의되지 않았다.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - 에러
     - 설명
     - HTTP Status Code
   * - ResourceNotFound
     - 지정된 자원이 존재하지 않습니다.
     - 404