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

To config rabbitmq, edit configuration file as below. The default config file 
path is "/etc/rabbitmq/rabbitmq.config". 

.. NOTE::

   Replace example hostname(synaps-mq01 and synaps-mq02) to real hostname. 

::

   [{rabbit, [{cluster_nodes, ['rabbit@synaps-mq01', 'rabbit@synaps-mq02']}]}].

