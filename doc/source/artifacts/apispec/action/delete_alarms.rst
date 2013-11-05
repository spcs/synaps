.. _delete_alarms:

DeleteAlarms
============

Description
-----------

It deletes all alarm that is specified in action parameter. If at least one 
AlarmName does not exist in the database, this action will not affect to any
alarm.  

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
     - List of alarm name to delete 
       Only Admin can call this action for the alarms that starts with "SPCS/".

       Data type: String list

       Limitation: 0 ~ 100
     - No

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
   * - ResourceNotFound
     - Requested alarms are not found 
     - 404
     
see also :ref:`common_errors` 
