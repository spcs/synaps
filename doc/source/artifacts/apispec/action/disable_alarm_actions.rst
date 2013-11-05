.. _disable_alarm_actions:

DisableAlarmActions
===================

Description
-----------
Deactivate the action of specific Alarm. In this case, Alarm action is not executed
even if Alarm state changed.

Parameters
----------

Following is list of parameters for this action.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - Name
     - Description
     - Mandatory
   * - AlarmNames.member.N
     - List of Alarm name to deactivate action. 
       Only Admin can call this action for the alarms that starts with "SPCS/". 

       Data type: String list

       Length limitation: 0 ~ 100 items.
     - Yes

see also :ref:`common_query_parameters` 
 
Error
-----

Following is list of errors for this action.

see also :ref:`common_errors` 
