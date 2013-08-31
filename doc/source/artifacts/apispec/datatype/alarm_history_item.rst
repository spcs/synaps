.. _alarm_history_item:

AlarmHistoryItem
================

Description
-----------
AlarmHistoryItem data type contain specified alarm's history information. If you 
call :ref:`describe_alarm_history`, SPCS Synaps will return this data type into
:ref:`describe_alarm_history_result` data type.

Contents
--------

Following is contents of this data type.

.. list-table:: 
   :widths: 30 50
   :header-rows: 1
   
   * - Name
     - Description
   * - AlarmName
     - Alarm's name.

       Data type: String

       Length limitation: 1 ~ 255 bytes
   * - HistoryData
     - Information for JSON-formatted Alarm. (for computer)

       Data type: String

       Length limitation: 1 ~ 4095 bytes
   * - HistoryItemType
     - Type of Alarm history.

       Data type: String

       Valid value: ConfigurationUpdate | StateUpdate | Action
   * - HistorySummary
     - Sumary of Alarm history. (for human)

       Data type: String

       Length limitation: 1 ~ 255 bytes
   * - Timestamp
     - Alarm history's timestamp

       Data type: DateTime
