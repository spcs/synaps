..
      Copyright 2012, 2013 Samsung SDS.
      All Rights Reserved.


Operational Manual
==================

This manual describes tips for operation.  

Starting Service Procedure
--------------------------

start storm topology

.. code-block:: bash

    sudo storm jar /SW/storm/synaps-storm.jar SynapsTopology 00


start synaps api

.. code-block:: bash
    
    sudo service synaps-api start

reload metric in memory 

.. code-block:: bash

    sudo synaps-reload-metric

Maintenance
-----------

How to perform minor upgrade without downtime
'''''''''''''''''''''''''''''''''''''''''''''

1. Upgrade Synaps pacakge for all servers

copy synaps-api build to all server and install the synaps-api package

.. code-block:: bash

    sudo pip install -U synaps-yyyy.xxxx.tar.gz

2. Restart synaps-api daemon

API servers can be configured Active-Active by Load balancer. So we can 
restart the API server side-by-side. 

.. code-block:: bash

    sudo service synaps-api restart

3. Restart synaps-storm(synaps00) topology

copy synaps-storm build to nimbus server and restart the topology and then,
reload the metrics.

Storm kill command takes about 30 seconds. Because it stops receiving message 
from the queue and consume all remaining messages within the 30 seconds. 

While the downtime of storm topology, all message are queued and can be 
processed when the storm topology is restarted.

.. code-block:: bash

    sudo /SW/storm/bin/storm kill synaps00
    sudo /SW/storm/bin/storm jar /SW/storm/synaps-storm.jar SynapsTopology 00
    sudo synaps-reload-metric

