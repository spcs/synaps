..
      Copyright 2012, 2013 Samsung SDS.
      All Rights Reserved.

Synaps API and topology
=======================

Synaps API
----------

To start, stop, restart and check status of API server.

.. code-block:: bash

	sudo service synaps-api start
	
.. code-block:: bash

	sudo service synaps-api stop
	
.. code-block:: bash

	sudo service synaps-api restart
	
.. code-block:: bash

	sudo service synaps-api status
	

Synaps topology
---------------

These operations can be done at nimbus node.
 
Starting topology
 
.. code-block:: bash

    user@nimbus$ sudo /SW/storm/bin/storm jar /SW/storm/synaps-storm.jar SynapsTopology
    user@nimbus$ sudo synaps-reload-metric


Stopping topology

.. code-block:: bash

    user@nimbus$ sudo /SW/storm/bin/storm kill synaps00


Re-balancing topology
	
.. code-block:: bash

    user@nimbus$ sudo /SW/storm/bin/storm rebalance synaps00
    user@nimbus$ sudo synaps-reload-metric

List all topology
	
.. code-block:: bash

	user@nimbus$ sudo /SW/storm/bin/storm list
	
Monitor topology status
	
.. code-block:: bash

	user@nimbus$ lynx localhost:8080


Minor upgrade procedure
-----------------------

When database scheme and internal RPC message formats are not changed, it can 
be upgrade in a procedure as below.
 
First, it is needed to upgrade synaps package. The procedure is not much 
different with another python packages. Copy synaps-api build to all server or
python package repository of your cloud and install the synaps-api package
using pip or easy_install tool.

.. code-block:: bash

    $ sudo pip install -U synaps-yyyy.xxxx.tar.gz

Then, restart API servers to apply the changes. If API servers are configured 
active-active by load balancer, it can be upgraded side-by-side. For example,
remove API group 1 from load balancer, wait about 1 minute for all requests
are processed, and add them to load balancer again. And then restart their api 
services. And then, do same procedure to other group.   

.. code-block:: bash
	
	# before stop the api service, remove apigroup1 from load balancer.	
	# wait enough...
	user@apigroup1 $ sudo service synaps-api restart
	# add apigroup1 and remove apigroup2 from load balancer
	# wait enough...
	user@apigroup2 $ sudo service synaps-api restart
    
To upgrade topology, copy topology jar file, kill old topology and submit new 
topology to nimbus. When stopping the topology, it stops to consume messages 
from queue and wait for 30 seconds to process all message not processed yet.

.. note::

    When starting the topology, it loads all active metric data from database 
    to memory. This operation costs a lot of CPU. So metric data processing can 
    be delayed. 
    
    Therefore it doesn't evaluates alarms to avoid false alarming at boot time. 
    After receiving three ack messages from all workers, it assumes that 
    system's status becomes stable and starts to evaluate alarms.   

.. code-block:: bash

    user@nimbus$ sudo storm kill synaps00
    # check if old topology is killed and disappears from list
    user@nimbus$ sudo watch storm list
    # submit new topology
    user@nimbus$ sudo storm jar /SW/storm/synaps-storm.jar SynapsTopology
    user@nimbus$ sudo synaps-reload-metric


After upgrade topology, it would be better to check the topology runs well with
`storm list` command. Result will be like below.

.. code-block:: none

	0    [main] INFO  backtype.storm.thrift  - Connecting to Nimbus at localhost:6627
	Topology_name        Status     Num_tasks  Num_workers  Uptime_secs
	-------------------------------------------------------------------
	synaps00             ACTIVE     76         6            7061


Logs
----

It generates large logs as it processes a lot of requests. So it is important 
to have enough disk spaces for logs and monitor if the space is still enough. 
The default log path is `/var/log/synaps`.

And if your workers in your topology are failing, check storm log files at 
`/var/log/storm` also.

