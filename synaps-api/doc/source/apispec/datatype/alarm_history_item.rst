.. _alarm_history_item:

AlarmHistoryItem
======================

설명
----
The AlarmHistoryItem data type contains descriptive information about the 
history of a specific alarm. If you call DescribeAlarmHistory, Amazon CloudWatch
returns this data type as part of the :ref:`describe_alarm_history_result` data type.

Contents
----

.. list-table:: 
   :widths: 15 50
   :header-rows: 1
   
   * - 이름
     - 설명
   * - AlarmName
     - The descriptive name for the alarm.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
   * - HistoryData
     - Machine-readable data about the alarm in JSON format.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 4095.
   * - HistoryItemType
     - The type of alarm history item.

       Type: String

       Valid Values: ConfigurationUpdate | StateUpdate | Action
   * - HistorySummary
     - A human-readable summary of the alarm history.

       Type: String

       Length constraints: Minimum length of 1. Maximum length of 255.
   * - Timestamp
     - The time stamp for the alarm history item.

       Type: DateTime
       
.. toctree::
   :maxdepth: 1 
   