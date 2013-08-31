
Build synaps-api and synaps-storm from source code
--------------------------------------------------


   
install synaps-storm
--------------------
  
For synaps-storm, you only need to copy synaps-storm build file(e.g. 
synaps-storm-yyyy.mm.xx.jar) to the Nimbus node. Because storm will deploy and 
distribute the build.



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

And then, need to set up cassandra for Synaps.

.. code-block:: bash

   sudo synaps-syncdb

Running Synaps
--------------

You can run synaps-api as a service on the web server.

.. code-block:: bash

   sudo service synaps-api start
   
You also can run synaps-noti to execute alarm action.

.. code-block:: bash

   sudo service synaps-noti start

To submit storm topology to Storm cluster,

.. code-block:: bash

   sudo storm jar synaps-storm-yyyy.mm.xx.jar com.spcs.synaps.PutMetricTopology topology_name
  
or you can run storm totpology local mode for devlopement.

.. code-block:: bash

   sudo storm jar synaps-storm-yyyy.mm.xx.jar com.spcs.synaps.PutMetricTopology


And then, need to set up cassandra for Synaps. (It can be done only once.)

.. code-block:: bash

   sudo synaps-syncdb

synaps-api, synaps-noti 배포
--------------------------

synaps-api 를 SPCS Synaps 저장소에서 다운받아 아래와 같이 설치한다.

.. code-block:: bash

  wget http://182.194.3.195:8080/synaps-package/product/synaps-yy.mm.dd.tar.gz 
  tar xvfz synaps-yy.mm.dd.tar.gz
  cd synaps-yy.mm.dd
  sudo python setup.py install
  
synaps-storm 배포
---------------

synaps-nimbus 노드에서 다음과 같이 synaps-storm 을 내려받아 아래와 같이 
실행하면 synaps-supervisor 에 자동으로 코드가 배포되고 실행된다. 

.. code-block:: bash

  wget http://182.194.3.195:8080/synaps-package/product/synaps-storm-yy.mm.dd.jar
  storm jar synaps-storm-yy.mm.dd.jar com.spcs.synaps.PutMetricTopology synapsstorm

Rabbit MQ
---------

Start and stop RabbitMQ

.. code-block:: bash

  rabbitmq-server -detached

.. code-block:: bash

  rabbitmqctl stop


Delete RabbitMQ database

.. code-block:: bash

  rm -rf /var/lib/rabbitmq/mnesia


Sync erlang.cookie file  ::

  Share same /var/lib/rabbitmq/.erlang.cookie file across nodes. 


To show cluster status

.. code-block:: bash

  rabbitmqctl cluster_status

  Cluster status of node 'rabbit@synaps-mq02' ...
  [{nodes,[{disc,['rabbit@(RabbitMQ1_HostName)','rabbit@synaps-mq01']}]},
  {running_nodes,['rabbit@(RabbitMQ2_HostName)','rabbit@synaps-mq02']}]
  ...done.

Storm
-----
    
Create symbolic link for log file directory.

.. code-block:: bash
  
   rm -rf /usr/local/storm/logs/
   mkdir /var/log/storm
   ln -s /var/log/storm /usr/local/storm/logs 


Register zookeeper as a service.

.. code-block:: bash

   ln -s /usr/share/zookeeper/bin/zkServer.sh /etc/init.d/

For Nimbus node, update rc.d as below. Before doing this, you need to install
synaps-api.

.. code-block:: bash

   sudo update-rc.d zkServer.sh defaluts 80 20  
   sudo update-rc.d storm-nimbus defaluts 81 19
   sudo update-rc.d storm-ui defaluts 82 18
      
For Supervisor node, update rc.d as below. Before doing this, you need to 
install synaps-api. 

.. code-block:: bash

   sudo update-rc.d zkServer.sh defaluts 80 20  
   sudo update-rc.d storm-supervisor defaluts 83 17
    


.. toctree::
    :maxdepth: 2
    
    operational/installation.guide.rst
    operational/deploy.synaps.rst      