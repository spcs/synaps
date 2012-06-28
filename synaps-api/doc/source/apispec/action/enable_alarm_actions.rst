.. _enable_alarm_actions:

EnableAlarmActions
======================

설명
----
Enables actions for the specified alarms.

요청 매개변수
-------------
For information about the common parameters that all actions use, see 
:ref:`common_query_parameters`.

.. list-table:: 
   :widths: 15 50 10
   :header-rows: 1

   * - 이름
     - 설명
     - 필수 여부
   * - AlarmNames.member.N
     - The names of the alarms to disable actions for.

       Type: String list

       Length constraints: Minimum of 0 item(s) in the list. Maximum of 100 
       item(s) in the list.
     - Yes
     
.. toctree::
   :maxdepth: 1