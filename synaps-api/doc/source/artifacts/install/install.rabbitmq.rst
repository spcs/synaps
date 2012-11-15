.. _install.rabbitmq:

Install RabbitMQ Example
========================

This document describes basic installation guide example. For more details, see 
http://www.rabbitmq.com/

.. NOTE::

   To provide HA, the version of rabbitmq should be greater than 2.8.4.

Download and install rabbitmq as below.

.. code-block:: bash

  dpkg -i rabbitmq-server_2.8.4_all.deb
  
Or, if your apt repository provides more recent version than 2.8.4; 

.. code-block:: bash
  
  sudo apt-get install rabbitmq-server

To config rabbitmq, edit configuration file as below. The default config file 
path is "/etc/rabbitmq/rabbitmq.config". 

.. NOTE::

   Replace example hostname(synaps-mq01 and synaps-mq02) to the first hostname 
   (the one without dots) of each server.
   For example, If hostname is "synapsmq1.exam.ple", only "synapsmq1" is used.  

::

   [{rabbit, [{cluster_nodes, ['rabbit@synaps-mq01', 'rabbit@synaps-mq02']}]}].

And all cluster must share same cookie file. Copy 
"/var/lib/rabbitmq/.erlang.cookie" from a node to all cluster nodes.

Now, you can start service as below.

.. code-block:: bash

   sudo service rabbit-server start
   
To verify if the rabbitmq is running well,

.. code-block:: bash

   $ rabbitmqctl cluster_status
   
   Cluster status of node 'rabbit@synaps-mq02' ...
   [{nodes,[{disc,['rabbit@synaps-mq02','rabbit@synaps-mq01']}]},
   {running_nodes,['rabbit@synaps-mq01','rabbit@synaps-mq02']}]
   ...done.
