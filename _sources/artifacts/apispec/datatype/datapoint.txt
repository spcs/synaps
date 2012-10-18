.. _datapoint:

Datapoint
=========

설명
----
SPCS Synaps 가 메트릭 데이터로 부터 계산한 통계 자료를 담는 자료형

내용
----

.. list-table:: 
   :widths: 30 50
   :header-rows: 1
   
   * - 이름
     - 설명
   * - Average
     - 메트릭 값의 평균

       자료 형: Double
   * - Maximum
     - 메트릭 값의 최대값

       자료 형: Double
   * - Minimum
     - 메트릭 값의 최소값

       자료 형: Double
   * - SampleCount
     - 메트릭 샘플의 갯수

       자료 형: Double
   * - Sum
     - 매트릭 샘플의 총 합

       자료 형: Double
   * - Timestamp
     - 데이터포인트가 사용하는 timestamp

       자료 형: DateTime
   * - Unit
     - 데이터포인트의 표준 단위

       자료 형: String

       유효 값: Seconds | Microseconds | Milliseconds | Bytes | Kilobytes | 
       Megabytes | Gigabytes | Terabytes | Bits | Kilobits | Megabits | 
       Gigabits | Terabits | Percent | Count | Bytes/Second | Kilobytes/Second | 
       Megabytes/Second | Gigabytes/Second | Terabytes/Second | Bits/Second | 
       Kilobits/Second | Megabits/Second | Gigabits/Second | Terabits/Second | 
       Count/Second | None
   