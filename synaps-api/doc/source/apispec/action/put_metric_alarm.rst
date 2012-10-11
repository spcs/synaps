.. _put_metric_alarm:

PutMetricAlarm
==============

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
     - 알람의 상태 변화에 따른 액션 수행 여부
       자료 형: Boolean
     - No
   * - AlarmActions.member.N
     - 알람 상태가 된 경우 SMS를 보낼 전화번호(국제전화번호 형식) 또는 전자우편
       을 보낼 E-Mail 주소를 입력한다.

       국제전화번호의 경우 +82 10 1234 5678 와 같은 형식을 따르며, 
       국제전화코드는 나머지 번호와 번호는 공백(' ')으로 구분되어야한다. 
       허용되는 문자열은 +, [0-9], 공백(' ') 으로 제한된다.
       
       International Telecommunication Union ITU-T Rec. E.123 (02/2001) 참조

       자료 형: String
     - No
   * - AlarmDescription	
     - 알람 설명

       자료 형: String

       길이 제한: 최소 1자 ~ 최대 255자
              
       형식 제한: 숫자로만 이루어진 값 사용 불가
     - No
   * - AlarmName
     - 알람 이름. 이 이름은 SPCS 프로젝트에 한해 유일해야한다.

       자료 형: String

       길이 제한: 최소 1자 ~ 최대 255자
              
       형식 제한: 숫자로만 이루어진 값 사용 불가
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
     
.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - 이름
     - 설명
     - 필수 여부
   * - EvaluationPeriods
     - 임계치 비교를 할 기간 (분 단위)

       자료 형: Integer
       
       유효 값: 1 ~ 100
     - Yes     
   * - InsufficientDataActions.member.N
     - 알람 상태가 Insufficient_Data가 된 경우 SMS를 보낼 전화번호(국제전화번호 
       형식) 또는 전자우편을 보낼 E-Mail 주소를 입력한다.

       국제전화번호의 경우 +82 10 1234 5678 와 같은 형식을 따르며, 
       국제전화코드는 나머지 번호와 번호는 공백(' ')으로 구분되어야한다. 
       허용되는 문자열은 +, [0-9], 공백(' ') 으로 제한된다.
       
       International Telecommunication Union ITU-T Rec. E.123 (02/2001) 참조

       자료 형: String
     - No
   * - MetricName
     - 알람에 관련된 메트릭의 이름

       자료 형: String

       길이 제한: 최소 1자 ~ 최대 255자
              
       형식 제한: 숫자로만 이루어진 값 사용 불가
     - Yes
   * - Namespace
     - 알람에 관련된 메트릭의 namespace

       자료 형: String

       길이 제한: 최소 1자 ~ 최대 255자
              
       형식 제한: 숫자로만 이루어진 값 사용 불가
     - Yes
   * - OKActions.member.N
     - 알람 상태가 OK로 변경된 경우 SMS를 보낼 전화번호(국제전화번호 형식) 또는 
       전자우편을 보낼 E-Mail 주소를 입력한다.

       국제전화번호의 경우 +82 10 1234 5678 와 같은 형식을 따르며, 
       국제전화코드는 나머지 번호와 번호는 공백(' ')으로 구분되어야한다. 
       허용되는 문자열은 +, [0-9], 공백(' ') 으로 제한된다.
       
       International Telecommunication Union ITU-T Rec. E.123 (02/2001) 참조

       자료 형: String
     - No
   * - Period
     - 통계가 적용될 기간(초 단위)

       자료 형: Integer
       
       유효값 : 60(1분) ~ 86400(24시간), 60의 배수.
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

       유효 값: Seconds | Microseconds | Milliseconds | Bytes | Kilobytes | 
       Megabytes | Gigabytes | Terabytes | Bits | Kilobits | Megabits | 
       Gigabits | Terabits | Percent | Count | Bytes/Second | Kilobytes/Second | 
       Megabytes/Second | Gigabytes/Second | Terabytes/Second | Bits/Second | 
       Kilobits/Second | Megabits/Second | Gigabits/Second | Terabits/Second | 
       Count/Second | None
     - No     
            
에러
----
공통으로 발생하는 에러는 :ref:`common_errors` 를 참고한다.
