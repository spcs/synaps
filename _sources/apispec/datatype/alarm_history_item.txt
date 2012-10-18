.. _alarm_history_item:

AlarmHistoryItem
================

설명
----
AlarmHistoryItem 자료 형은 특정 알람의 히스토리 정보를 포함한다. 
:ref:`describe_alarm_history` 를 호출하면 SPCS Synaps 는 이 자료 형을
:ref:`describe_alarm_history_result` 자료 형에 포함해서 돌려준다.

내용
----

.. list-table:: 
   :widths: 30 50
   :header-rows: 1
   
   * - 이름
     - 설명
   * - AlarmName
     - 알람 이름

       자료 형: String

       길이 제한: 최소 1자 부터 255자
   * - HistoryData
     - JSON 형식의 알람에 대한 정보 (기계가 읽기 위한 용도)

       자료 형: String

       길이 제한: 최소 1자 부터 4095자
   * - HistoryItemType
     - 알람 히스토리 종류

       자료 형: String

       유효 값: ConfigurationUpdate | StateUpdate | Action
   * - HistorySummary
     - 알람 히스토리의 요약 (사람이 읽기 편한 형식)

       자료 형: String

       길이 제한: 최소 1자 부터 255자
   * - Timestamp
     - 알람 히스토리 항목의 timestamp

       자료 형: DateTime
