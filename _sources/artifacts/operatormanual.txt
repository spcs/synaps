..
      Copyright 2012 Samsung SDS.
      All Rights Reserved.


Operational Manual
==================

This manual describes tips for operation.  

Starting Service Procedure
--------------------------

start storm topology

.. code-block:: bash

    sudo storm jar /SW/storm/synaps-storm.jar com.spcs.synaps.PutMetricTopology 00


start synaps api

.. code-block:: bash
    
    sudo service synaps-api start

reload metric in memory 

.. code-block:: bash

    sudo synaps-reload-metric

Maintenance
-----------

TBD

