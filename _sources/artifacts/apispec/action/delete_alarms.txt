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

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - Name
     - Description
     - Mandatory
   * - AlarmNames.member.N
     - List of alarm name to delete 

       Data type: String list

       Limitation: 0 ~ 100
     - No

see also :ref:`common_query_parameters` 

Errors
------

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
