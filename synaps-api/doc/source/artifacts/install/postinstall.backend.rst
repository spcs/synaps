.. _postinstall.backend:

Post-installation Synaps backend
--------------------------------

Register zookeeper /etc/init.d

.. code-block:: bash

   ln -s /usr/share/zookeeper/bin/zkServer.sh /etc/init.d/

For Nimbus node(synaps01), update rc.d as below.

.. code-block:: bash

   sudo update-rc.d zkServer.sh defaluts 80 20  
   sudo update-rc.d storm-nimbus defaluts 81 19
   sudo update-rc.d storm-ui defaluts 82 18
   sudo update-rc.d synaps-noti defaluts 80
      
For Supervisor nodes(synaps02 ~ nn), update rc.d as below. 

.. code-block:: bash

   sudo update-rc.d zkServer.sh defaluts 80 20  
   sudo update-rc.d storm-supervisor defaluts 83 17
    