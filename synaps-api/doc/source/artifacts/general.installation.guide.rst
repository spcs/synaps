.. _general.installation.guide:

Installation Guide
==================

This instruction describes how to install Synaps. It assumes that you are 
familiar with GIT and Ubuntu.

Pre-installation Requirements
-----------------------------

You need to install softwares listed belows. You can install all of them on 
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

Install Synaps from Github
--------------------------

'synaps' module should be installed for all of your Synaps WSGI Web Servers 
and Storm nodes. see :ref:`install.synaps.api.ubuntu` for more easy guide for Ubuntu.  

.. code-block:: bash

  git clone https://github.com/spcs/synaps.git
  cd synaps/synaps-api
  sudo python setup.py install
  
Next, you should build synaps-storm topology.

.. code-block:: bash

  cd synaps/synaps-storm
  mvn package

Then, synaps-storm-yyyy.mm.xx.jar file could be found under 
synaps/synaps-storm/target directory.


Running Synaps
--------------

Once you install the python 'synaps' module, you can run WSGI web server just 
like below. 

.. code-block:: bash

  synaps-api-cloudwach
  
or you can run synaps-api as a service.

.. code-block:: bash

  service synaps-api start

To submit storm topology to Storm cluster,

.. code-block:: bash

  storm jar synaps-storm-yyyy.mm.xx.jar com.spcs.synaps.PutMetricTopology topology_name
  
or you can run storm totpology local mode.

.. code-block:: bash

  storm jar synaps-storm-yyyy.mm.xx.jar com.spcs.synaps.PutMetricTopology
