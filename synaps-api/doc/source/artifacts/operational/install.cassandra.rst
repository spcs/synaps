.. _install.cassandra:

Install Cassandra Example
-------------------------

This document describes basic installation guide example. For more details, see 
http://cassandra.apache.org/


Download cassandra and unzip the tarball.

.. code-block:: bash

  tar xvfz apache-cassandra-1.0.8-bin.tar.gz /usr/local/

To config cassandra, edit configuration file as below. The default config file
path is "/usr/local/apache-cassandra-1.0.8/conf/cassandra.yaml"

.. NOTE::

  Set 'seeds' as all your cassandra node list and 'listen_address' as hostname 
  of local machine. 

.. code-block:: bash

   cluster_name: 'Synaps Product Cluster'
   
   # directories where Cassandra should store data on disk.
   data_file_directories:
       - /var/log/cassandra/data
   
   # commit log
   commitlog_directory: /var/log/cassandra/commitlog
   
   # saved caches
   saved_caches_directory: /var/log/cassandra/saved_caches
   
   seed_provider:
       # Addresses of hosts that are deemed contact points.
       # Cassandra nodes use this list of hosts to find each other and learn
       # the topology of the ring.  You must change this if you are running
       # multiple nodes!
       - class_name: org.apache.cassandra.locator.SimpleSeedProvider
         parameters:
             # seeds is actually a comma-delimited list of addresses.
             # Ex: "<ip1>,<ip2>,<ip3>"
             - seeds: "(Cassandra_HostName1),(Cassandra_HostName2),(Cassandra_HostName3)"
   
   # Setting this to 0.0.0.0 is always wrong.
   listen_address: (Local_HostName)
   
   rpc_address: 0.0.0.0
