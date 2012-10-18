.. _metric_datum:

MetricDatum
===========

설명
----
:ref:`put_metric_data` 를 통해 보낼 정보. 새로운 메트릭을 생성하거나 기존
메트릭에 새로운 값을 추가하기 위해 사용함.

내용
----

.. list-table:: 
   :widths: 30 50
   :header-rows: 1
   
   * - 이름
     - 설명
   * - Dimensions
     - 메트릭의 dimensions

       자료 형: :ref:`dimension` 리스트

       길이 제한: 최소 0개, 최대 10개의 아이템
   * - MetricName
     - 메트릭 이름

       자료 형: String

       길이 제한: 최소 1자, 최대 255자
   * - StatisticValues
     - TBD - 아직 구현되지 않음
   * - Timestamp
     - 메트릭에 대응하는 timestamp. 지정되지 않은 경우 기본 값으로 메트릭을 
       입력받은 시간을 사용한다.

       자료 형: DateTime
   * - Unit
     - 메트릭의 단위

       자료 형: String

       유효 값: Seconds | Microseconds | Milliseconds | Bytes | Kilobytes | 
       Megabytes | Gigabytes | Terabytes | Bits | Kilobits | Megabits | 
       Gigabits | Terabits | Percent | Count | Bytes/Second | Kilobytes/Second | 
       Megabytes/Second | Gigabytes/Second | Terabytes/Second | Bits/Second | 
       Kilobits/Second | Megabits/Second | Gigabits/Second | Terabits/Second | 
       Count/Second | None
   * - Value
     - 메트릭의 값

       자료 형: Double
