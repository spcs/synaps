.. _metric_alarm:

MetricAlarm
===========

설명
----
:ref:`metric_alarm` 자료형은 알람을 나타낸다. :ref:`put_metric_alarm` 액션으로 
알람을 생성하고 갱신할 수 있다.

내용
----

.. list-table:: 
   :widths: 30 50
   :header-rows: 1
   
   * - 이름
     - 설명
   * - ActionsEnabled
     - TBD - 아직 구현되지 않음

       자료 형: Boolean
   * - AlarmActions
     - TBD - 아직 구현되지 않음
   * - AlarmArn
     - 알람의 자원 번호

       자료 형: String

       길이 제한: 최소 1자, 최대 1000자
   * - AlarmConfigurationUpdatedTimestamp
     - 알람 설정이 변경된 가장 최근의 시간 

       자료 형: DateTime
   * - AlarmDescription
     - 알람 설명

       자료 형: String

       길이 제한: 최소 0자, 최대 255자
   * - AlarmName
     - 알람 이름

       자료 형: String

       길이 제한: 최소 1자, 최대 255자
   * - ComparisonOperator
     - 특정 통계 자료와 임계치를 비교하기 위해 사용하는 산술 연산자. 통계 자료
       가 좌변 변수로 적용 된다. 

       자료 형: String

       유효 값: GreaterThanOrEqualToThreshold | GreaterThanThreshold |
       LessThanThreshold | LessThanOrEqualToThreshold
   * - Dimensions
     - 알람 대상 메트릭의 dimensions 리스트

       자료 형: :ref:`dimension` 리스트

       길이 제한: 0개부터 10개의 아이템
   * - EvaluationPeriods
     - 임계치와 비교할 데이터의 갯수

       자료 형: Integer
   * - InsufficientDataActions
     - TBD - 아직 구현되지 않음
   * - MetricName
     - 알람 대상 메트릭의 이름

       자료 형: String

       길이 제한: 최소 1자, 최대 255자
   * - Namespace
     - 알람 대상 메트릭의 namespace

       Type: String

       길이 제한: 최소 1자, 최대 255자
   * - OKActions
     - TBD - 아직 구현되지 않음
   * - Period
     - 통계 자료 계산에 적용될 기간 (초단위) 

       자료 형: Integer

.. list-table:: cont' 
   :widths: 30 50
   :header-rows: 1
   
   * - 이름
     - 설명       
   * - StateReason
     - 알람 상태의 이유 (사람이 읽기 좋은 형식)

       자료 형: String

       길이 제한: 최소 0자, 최대 1023자
   * - StateReasonData
     - 알람 상태의 이유 (JSON 형식)

       자료 형: String

       길이 제한: 최소 0자, 최대 4000자
   * - StateUpdatedTimestamp
     - 알람의 상태가 변경된 최근의 timestamp

       자료 형: DateTime
   * - StateValue
     - 알람의 상태 값

       자료 형: String

       유효 값: OK | ALARM | INSUFFICIENT_DATA
   * - Statistic
     - 알람 대상 메트릭의 통계

       자료 형: String

       유효 값: SampleCount | Average | Sum | Minimum | Maximum
   * - Threshold
     - 통계자료와 비교할 임계치

       자료 형: Double
   * - Unit
     - 알람 대상 메트릭의 단위

       자료 형: String

       유효 값: Seconds | Microseconds | Milliseconds | Bytes | 
       Kilobytes | Megabytes | Gigabytes | Terabytes | Bits | Kilobits | 
       Megabits | Gigabits | Terabits | Percent | Count | Bytes/Second | 
       Kilobytes/Second | Megabytes/Second | Gigabytes/Second | 
       Terabytes/Second | Bits/Second | Kilobits/Second | Megabits/Second | 
       Gigabits/Second | Terabits/Second | Count/Second | None

   