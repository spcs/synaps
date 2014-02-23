README for Synaps
=================

Synaps is a cloud monitoring system, Monitoring as a service.

* Documentation: http://spcs.github.com/synaps
* Issue Tracking: http://launchpad.net/synaps


Release Notes
-------------

version 2013.2.3
~~~~~~~~~~~~~~~~

New Features

* Group notification alarm action is added - Notify to pre-defined user group 
* Instance action alarm action is added - Reboot or migrate your nova VM 
  instance when alarm status is changed
* Dimensions filter is introduced to search metrics more efficiently 
* Supports OpenStack Keystone
* Metering alarms, metrics and alarm actions 
* Project alarm quota is introduced
* Parallel integrated test cases are included
* Stress test cases are included  
* Warm up period is introduced
* Storm log is now using common logging module

Bug fixes

* State updated timestamp of a newly created alarm is expected in UTC but is in 
  localtime. (test case added)
* UnboundLocalError: local variable 'stat' referenced before assignment in the
  put metric bolt.
* Unauthorized error is returned in form of XML so that SDK can parse error 
  code. 


version 2012.09.b6-2 (2012-11-27)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Upgrade Storm version from 0.8.0 to 0.8.1.

version 2012.09.b6 (2012-11-20)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Initially Released.
