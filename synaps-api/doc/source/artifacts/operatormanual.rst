..
      Copyright 2012 Samsung SDS.
      All Rights Reserved.


Operational Manual
==================

This manual describes tips for operation.  


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