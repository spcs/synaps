.. _describe_alarm_history:

DescribeAlarmHistory
======================

Description
----
Check the history of specific Alarm. You can search history using Period or
HistoryItemType. If you don't specify AlarmName, Synaps will return history
information of all Alarms that user has.

Note:
  SPCS Synaps stores AlarmHistory for 2 weeks whether alarm is deleted or not.

Parameters
-------------

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - Name
     - Description
     - Mandatory
   * - AlarmName	
     - Alarm name.
       
       Data type: String
       
       Length limitation: 1 ~ 255 bytes
              
       Type limitation: Value consisting of only numbers can not be used.
     - No
   * - EndDate	
     - End of the period for which you want to check the AlarmHistory.
       
       Data type: DateTime
     - No
   * - HistoryItemType	
     - Type of AlarmHistory to check.
      
       Data type: String
      
       Valid values: ConfigurationUpdate | StateUpdate | Action
     - No
   * - MaxRecords	
     - Max number of AlarmHistory to check.
      
       Data type: Integer
     - No
   * - NextToken	
     - Token to check next data.
       
       Data type: String
     - No
   * - StartDate	
     - Start period for which you want to check the AlarmHistory.
       
       Data type: DateTime
     - No

see also :ref:`common_query_parameters` 

Response
----
Following elements are structured in :ref:`describe_alarm_history_result` and returned.

.. list-table:: 
   :widths: 30 50
   :header-rows: 1

   * - Name
     - Description
   * - AlarmHistoryItems
     - JSON-Formatted AlarmHistory.
       
       Data type: :ref:`alarm_history_item` list
   * - NextToken
     - Token to check next data.
       
       Data type: String

Errors
----

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1
   
   * - Error
     - Description
     - HTTP Status Code
   * - InvalidNextToken
     - Invalid next token.
     - 400

see also :ref:`common_errors` 
