.. _general.installation.guide:

Installation Guide
==================

This instruction describes how to install Synaps. It assumes that you are 
familiar with GIT and Ubuntu.

Pre-installation Requirements
-----------------------------

You need to install softwares listed below. You can install all of them on 
the single machine for development or multiple nodes.
 
* Cassandra 1.0.8 - http://cassandra.apache.org/
* Storm 0.8.0 - http://storm-project.net/
* RabbitMQ - http://www.rabbitmq.com/
* Memcached (only for WSGI Web Server nodes)
* JDK and Maven2 (only for build storm topology)   

And for each Storm and WSGI Web Server nodes, you will need python packages 
listed below.

* setuptools
* eventlet
* pastedeploy
* gflags
* netaddr
* python-memcache
* numpy
* webob
* ldap
* zmq
* dateutil-1.5
* pandas-0.7.3 (currently, it doesn't support more recent version)  
* thrift-0.8.0
* pycassa-1.5.1
* pika-0.9.5
* boto-2.5.3

Build synaps-api and synaps-storm from source code
--------------------------------------------------

You need to build synaps-api and synaps-storm programs. The synaps-api should
be installed for all of your Synaps web servers and Storm nodes.

.. code-block:: bash

  git clone https://github.com/spcs/synaps.git
  cd synaps/synaps-api
  python setup.py sdist
  
Then, synaps-yy.mm.xx.tar.gz file can be found under "synaps/synaps-api/dist"
directory.   
  
Next, you should build synaps-storm topology.

.. code-block:: bash

  cd synaps/synaps-storm
  mvn package

Then, synaps-storm-yyyy.mm.xx.jar file could be found under 
synaps/synaps-storm/target directory.

Install synaps-api and synaps-storm
-----------------------------------

Copy synaps-api build file(e.g. synaps-yy.mm.xx.tar.gz) to every Synaps web 
servers and synaps storm machine.

and install it.

.. code-block:: bash

  tar xvfz synaps-yy.mm.xx.tar.gz
  cd synaps/synaps-api
  sudo python setup.py install
  
For synaps-storm, you only need to copy synaps-storm build file(e.g. 
synaps-storm-yyyy.mm.xx.jar) to the Nimbus node. Because storm will deploy and 
distribute the build.

Configuration
-------------

To configure Synaps, you'll need to make configuration directory. The default
path is "/etc/synaps". Those configuration files should be identical across the 
web servers and storm nodes.

.. code-block:: bash

   sudo mkdir /etc/synaps
   
And then, create or edit "synaps.conf" file. Following is an example.

.. code-block:: bash

   [DEFAULT]
   cassandra_server_list = cassandra1:9160,cassandra2:9160,cassandra3:9160
   cassandra_keyspace = synaps
   cassandra_replication_factor = 3
   # 30 days in seconds
   statistics_ttl = 2592000
   
   log_dir = /var/log/synaps/
   api_paste_config = /etc/synaps/api-paste.ini
   
   ### rabbit mq configuration
   rabbit_host = rabbitmq_host
   
   smtp_server = mail.product
   mail_sender = synaps@my.openstack
   notification_bind_addr = tcp://*:31110
   notification_server_addr = tcp://synapsnoti:31110

Next, you'll need to create "api-paste.ini" like below for setting up the WSGI 
pipeline. 

.. code-block:: bash
  
   ##############
   # CloudWatch #
   ##############
   
   [composite:cloudwatch]
   use = egg:Paste#urlmap
   /monitor: cloudwatch_api_v1
   
   [pipeline:cloudwatch_api_v1]
   #pipeline = fault_wrap log_request no_auth monitor_request authorizer cloudwatch_executor
   pipeline = fault_wrap log_request authenticate monitor_request authorizer cloudwatch_executor
   
   [filter:fault_wrap]
   paste.filter_factory = synaps.api.cloudwatch:FaultWrapper.factory
   
   [filter:log_request]
   paste.filter_factory = synaps.api.cloudwatch:RequestLogging.factory
   
   [filter:no_auth]
   paste.filter_factory = synaps.api.cloudwatch:NoAuth.factory
   
   [filter:authenticate]
   paste.filter_factory = synaps.api.cloudwatch:Authenticate.factory
   
   [filter:monitor_request]
   controller = synaps.api.cloudwatch.monitor.MonitorController
   paste.filter_factory = synaps.api.cloudwatch:Requestify.factory
   
   [filter:authorizer]
   paste.filter_factory = synaps.api.cloudwatch:Authorizer.factory
   
   [app:cloudwatch_executor]
   paste.app_factory = synaps.api.cloudwatch:Executor.factory

You need to make directory for log file. Default path is "/var/log/synaps".

.. code-block:: bash

   sudo mkdir /var/log/synaps

And then, need to set up cassandra for Synaps.

.. code-block:: bash

   sudo synaps-syncdb


Running Synaps
--------------

You can run synaps-api as a service.

.. code-block:: bash

   sudo start synaps-api

To submit storm topology to Storm cluster,

.. code-block:: bash

   sudo storm jar synaps-storm-yyyy.mm.xx.jar com.spcs.synaps.PutMetricTopology topology_name
  
or you can run storm totpology local mode for devlopement.

.. code-block:: bash

   sudo storm jar synaps-storm-yyyy.mm.xx.jar com.spcs.synaps.PutMetricTopology
