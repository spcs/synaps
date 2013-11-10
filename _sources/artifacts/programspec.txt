..
      Copyright 2012 Samsung SDS.
      All Rights Reserved.


Program Specification
=====================

Synaps is a cloud monitoring system that collects metric data, provides 
statistics data, monitors and notifies based on user defined alarms.

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
actions. It should evaluate alarms periodically and invoke actions, such as
sending email, SMS or rebooting or migrating a VM instance when its status is 
changed.

Users can describe histories of alarms so that they can know the information 
about the alarm creation, transition of its status and histories of alarm 
actions.

Program Architecture
--------------------

If there are 1,000 VM instances in your cloud, and 10 metrics per instance are
inputed to the Synaps, it should process 10,000 metrics in a minute. And if 
your cloud runs well, you would have more VMs. So it should be distributed and 
scalable.

Synaps API is frontend of the system. Keystone can be integrated for 
authentication as well as LDAP. It uses RabbitMQ for asynchronous messaging. 

Synaps topology runs on the Twitter Storm, the real-time distributed stream 
processing system. Storm manages distributing workers in the topology and 
handles failed workers.

The topology pulls messages from the queue, aggregates metric data and 
evaluates alarms in-memory, and write the result into Cassandra database. So 
that it helps reducing read operations that cost a lot. It invokes actions when 
the status of alarm has been changed. It can be integrated with mail server and 
SMS agents to send notifications to user-specified contact list and Nova API to 
reboot or migrate specified VMs.

Cassandra no-sql database is used for storing persistent data which is 
massively fast for writing operation and provides good availability and 
scalability. Deploying Cassandra and synaps-topology together can be a good 
choice for performance. 

Each component of Synaps is linear scalable. 

.. figure:: ../images/diagrams/SynapsSystemOverview.jpg
   :width: 100%
   
   Synaps Architecture Overview
      

Synaps provides AWS CloudWatch compatible API so that users can use the SDKs
for AWS CW for Synaps also. Internally, it can be integrated with your agent
for your cloud services so that users can monitor their resource in the cloud.   

For example, VMMON which can get information from VM Hyperisor via libvirt APIs
and Nova API and put metric data to Synaps so that users can utilize the data. 
But such agents are not in the scope of Synaps project.

.. figure:: ../images/diagrams/IntegratedSystemOverview.jpg
   :width: 100%

   Synaps Integration Example


Program: Synaps API
-------------------

Synaps API is WSGI based Web Server which provides AWS CloudWatch compatible 
API.

Asynchrous request processing
+++++++++++++++++++++++++++++

Requests below are processed asynchrously. 

* DeleteAlarms
* PutMetricAlarm
* PutMetricData

For example,
  
 .. image:: ../images/diagrams/SynapsAPI-PutMetricData.jpg
   :width: 100%
   
   
Synchrous request processing
++++++++++++++++++++++++++++

Requests below are processed synchrously.
      
* DescribeAlarmHistory
* DescribeAlarms
* DescribeAlarmsForMetric
* DisableAlarmActions
* EnableAlarmActions
* GetMetricStatistics
* ListMetrics
* SetAlarmState

For example,

 .. image:: ../images/diagrams/SynapsAPI-GetMetricStatistics.jpg
   :width: 100%

Program: Synaps Storm
---------------------

Synaps Storm is a topology implementation which is aimed to run on the Twitter 
Storm, real-time distributed stream processing system.  

 .. image:: ../images/diagrams/SynapsStorm-Topology.jpg
   :width: 100%

PutMetricData message processing
++++++++++++++++++++++++++++++++

This function is the most important part of Synaps. When the PutMetricData 
message is received via RabbitMQ message queue, it reads its in-memory sliding 
windows or database to aggregate its datapoints and evalutate status of 
its alarms. If the status is changed, it sends action message to notification 
queue.
   
 .. image:: ../images/diagrams/SynapsStorm-PutMetricData.jpg
   :width: 100%

PutMetricAlarm message processing
+++++++++++++++++++++++++++++++++

When the PutMetricAlarm message is received via RabbitMQ message queue, it
find its metric and update its in-memory alarm data and update it into 
database. 
   
 .. image:: ../images/diagrams/SynapsStormPutMetricAlarm.jpg
   :width: 100%

PeriodicMonitoring message processing
+++++++++++++++++++++++++++++++++++++

'check_spout' generates PeriodicMonitoring message every 1 minute. When this is
generated, it checks their whole alarms if they are not evaluated alarms 
recently PutMetricData message processing.

 .. image:: ../images/diagrams/SynapsStormPeriodicMonitoring.jpg
   :width: 100%
