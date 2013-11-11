..
      Copyright 2012 Samsung SDS.
      All Rights Reserved.

Synaps
======

Overview
--------

Synaps is a cloud monitoring system that collects metric data, provides 
statistics data, monitors and notifies based on user defined alarms.

* Linear scalable
* AWS CloudWatch API compatible
* Real-time monitoring system

Requirements
------------

It should provide an interface for another services in the cloud to put their
metric data of user resources such as VM instances, software load-balancers, 
RDS instances, Hadoop batch jobs, etc. And using that interface, users also can
put their own metric data that service provider doesn't provide.

It should aggregate all metric data into time frames of 1 minute, and should
provide interfaces to retrieve metric list and statistics data so that users 
can utilize metric data of their resources in the cloud.

Users can create alarms that contains evaluation criteria, periods and alarm
actions. It should evaluate alarms periodically and when the threshold is 
crossed, it should invoke actions, such as sending email, SMS or rebooting or 
migrating a VM instance as described in the alarm.

Users can also describe histories of alarms so that they can know the 
information about the alarm creation, transition of its status and histories of 
alarm actions.

Artifacts
---------

.. toctree::
    :maxdepth: 3
 
    artifacts/programspec.rst    
    artifacts/dbmodel.rst
    artifacts/apispec.rst
    artifacts/sdkdescription.rst
    artifacts/usermanual.rst
    artifacts/build.guide.rst
    artifacts/general.installation.guide.rst
    artifacts/operatormanual.rst
    artifacts/developersguide.rst

Indices
-------
    
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`    
