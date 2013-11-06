.. _set_alarm_state:

SetAlarmState
=============

Description
-----------
Set state of Alarm temporary. State is not continue; changed to the actual state
when the following alarm checking.

Parameters
----------

Following is list of parameters for this action.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - Name
     - Description
     - Mandatory
   * - AlarmName
     - name of Alarm. It should be unique in user's all alarm.
       Only Admin can call this action for the alarms that starts with "SPCS/". 

       Data type: String

       Length limitation: 1 ~ 255 bytes
              
       Type limitation: Value consisting of only numbers can not be used.
     - Yes
   * - StateReason
     - Reason for the alarm state has changed in the friendly human-readable
       text form.

       Data type: String

       Length limitation: 1 ~ 1203 bytes
              
       Type limitation: Value consisting of only numbers can not be used.
     - Yes
   * - StateReasonData
     - Reason for the alarm state has changed in the JSON format.

       Data type: String

       Length limitation: 0 ~ 4000 bytes
              
       Type limitation: Value consisting of only numbers can not be used.
     - No
   * - StateValue
     - State value.

       Data type: String

       Valid value: OK | ALARM | INSUFFICIENT_DATA
     - Yes       

see also :ref:`common_query_parameters`   
     
Errors
------

Following is list of errors for this action.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1
   
   * - Error
     - Description
     - HTTP Status Code
   * - InvalidFormat
     - Invalid JSON format data.
     - 400  
   * - ResourceNotFound
     - Alarm name that does not exist.
     - 404

see also :ref:`common_errors` 