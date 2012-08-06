.. _put_metric_alarm:

PutMetricAlarm
======================

설명
----
메트릭에 대해 알람을 생성하거나 업데이트한다. 

요청 매개변수
-------------
공통으로 요구되는 매개변수는 :ref:`common_query_parameters` 를 참고한다.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - 이름
     - 설명
     - 필수 여부
   * - ActionsEnabled
     - TBD - 아직 구현되지 않음
     - No
   * - AlarmActions.member.N
     - TBD - 아직 구현되지 않음
     - No
   * - AlarmDescription	
     - 알람 설명

       자료 형: String

       길이 제한: 최소 1자 ~ 최대 255자
     - No
   * - AlarmName
     - 알람 이름. 이 이름은 SPCS 프로젝트에 한해 유일해야한다.

       자료 형: String

       길이 제한: 최소 1자 ~ 최대 255자
     - Yes

   * - ComparisonOperator
     - 임계치와 비교할 연산자. 통계 자료가 좌변 연산 값으로 사용된다.

       자료 형: String

       유효 값: GreaterThanOrEqualToThreshold | GreaterThanThreshold | 
       LessThanThreshold | LessThanOrEqualToThreshold
     - Yes     
   * - Dimensions.member.N
     - 알람에 관련된 메트릭의 dimensions

       자료 형: :ref:`dimension` 리스트

       길이 제한: 최소 0개부터 최대 10개의 아이템
     - No     
   * - EvaluationPeriods
     - 임계치 비교를 할 데이터의 횟수

       자료 형: Integer
     - Yes     
   * - InsufficientDataActions.member.N
     - TBD - 아직 구현되지 않음
     - No
   * - MetricName
     - 알람에 관련된 메트릭의 이름

       자료 형: String

       길이 제한: 최소 1자 ~ 최대 255자
     - Yes
   * - Namespace
     - 알람에 관련된 메트릭의 namespace

       자료 형: String

       길이 제한: 최소 1자 ~ 최대 255자
     - Yes
   * - OKActions.member.N
     - TBD - 아직 구현되지 않음
     - No
   * - Period
     - 통계가 적용될 기간(초 단위)

       자료 형: Integer
     - Yes     
   * - Statistic
     - 알람에 사용할 메트릭의 통계

       자료 형: String

       유효 값: SampleCount | Average | Sum | Minimum | Maximum
     - Yes     
   * - Threshold
     - 통계자료와 비교할 임계치.

       자료 형: Double
     - Yes     
   * - Unit
     - 알람과 연계된 메트릭의 단위.

       자료 형: String

       Valid Values: Seconds | Microseconds | Milliseconds | Bytes | Kilobytes | 
       Megabytes | Gigabytes | Terabytes | Bits | Kilobits | Megabits | 
       Gigabits | Terabits | Percent | Count | Bytes/Second | Kilobytes/Second | 
       Megabytes/Second | Gigabytes/Second | Terabytes/Second | Bits/Second | 
       Kilobits/Second | Megabits/Second | Gigabits/Second | Terabits/Second | 
       Count/Second | None
     - No     
            
에러
----
공통으로 발생하는 매개변수는 :ref:`common_errors` 를 참고한다.
