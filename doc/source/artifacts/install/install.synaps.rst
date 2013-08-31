.. _install.synaps:

Install Synaps module
=====================

Pre-installation Requirements
-----------------------------

You will need python packages listed below.

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
* pycrypto
* pika-0.9.6
* boto-2.5.2

Following is a pre-installation example for Ubuntu 12.04.

.. code-block:: bash

   # install apt packages
   sudo apt-get install build-essential python-dev memcached
   sudo apt-get install python-setuptools python-eventlet python-pastedeploy 
   sudo apt-get install git python-gflags python-netaddr python-memcache
   sudo apt-get install python-numpy python-webob python-ldap
   sudo apt-get install python-mysqldb
   
   # download 3rd-party packages
   mkdir /tmp/packages
   cd /tmp/packages
   wget http://labix.org/download/python-dateutil/python-dateutil-1.5.tar.gz
   wget http://pypi.python.org/packages/source/p/pandas/pandas-0.7.3.tar.gz#md5=e4876ea5882accce15f6f37750f3ffec
   wget http://pypi.python.org/packages/source/t/thrift/thrift-0.8.0.tar.gz
   wget https://github.com/downloads/pycassa/pycassa/pycassa-1.5.1.tar.gz
   wget http://ftp.dlitz.net/pub/dlitz/crypto/pycrypto/pycrypto-2.6.tar.gz
   wget http://pypi.python.org/packages/source/p/pika/pika-0.9.6.tar.gz
   wget https://github.com/downloads/boto/boto/boto-2.5.2.tar.gz
   
   # unzip packages
   tar xvfz python-dateutil-1.5.tar.gz
   tar xvfz pandas-0.7.3.tar.gz
   tar xvfz thrift-0.8.0.tar.gz
   tar xvfz pycassa-1.5.1.tar.gz
   tar xvfz pycrypto-2.6.tar.gz
   tar xvfz pika-0.9.6.tar.gz
   tar xvfz boto-2.5.2.tar.gz
   
   # install python-dateutil 1.5
   cd python-dateutil-1.5
   sudo python setup.py install
   cd ..   

   # install pandas 0.7.3
   cd pandas-0.7.3/
   sudo python setup.py install
   cd ..
   
   # install thrift
   cd thrift-0.8.0
   sudo python setup.py install
   cd ..
   
   # install pycassa
   cd pycassa-1.5.1
   sudo python setup.py install
   cd ..
   
   # install pycrypto
   cd pycrypto-2.6
   sudo python setup.py install
   cd ..
   
   # install pika  
   cd pika-0.9.6
   sudo python setup.py install
   cd ..

   # install boto  
   cd boto-2.5.2
   sudo python setup.py install
   cd ..

Installation
------------

Copy synaps-api build file(e.g. synaps-yy.mm.xx.tar.gz) and install it as below.

.. code-block:: bash

  tar xvfz synaps-yy.mm.xx.tar.gz
  cd synaps/synaps-api
  sudo python setup.py install


Configuration
-------------

To configure Synaps, you'll need to make configuration directory. The default
path is "/etc/synaps". *Those configuration files should be identical across the 
web servers and storm nodes.*

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
   pipeline = fault_wrap log_request no_auth monitor_request authorizer cloudwatch_executor
   #pipeline = fault_wrap log_request authenticate monitor_request authorizer cloudwatch_executor
   
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