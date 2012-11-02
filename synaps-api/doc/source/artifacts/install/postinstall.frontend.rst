.. _postinstall.frontend:

Post-installation Synaps frontend
---------------------------------

To adjust maximum open files.

.. code-block:: bash

   sudo ulimit -Hn 65535
   sudo ulimit -Sn 65535
  
edit '/etc/security/limits.conf' file

.. code-block:: bash
  
   root            hard    nofile          65535
   root            soft    nofile          65535

Update rc.d

.. code-block:: bash

   sudo update-rc.d synaps-api defaults 80

Run synaps-api

.. code-block:: bash

   sudo service synaps-api start

Then, you would have four synaps-cloudwatch-api processes running.

.. code-block:: bash

   $ ps -ef | grep synaps-api-cloudwatch
   root      1004     1  2 15:52 ?        00:08:19 /usr/bin/python /usr/local/bin/synaps-api-cloudwatch --cloudwatch_listen_port=8776 --logfile=synaps-api-1.log
   root      1008     1  1 15:52 ?        00:07:50 /usr/bin/python /usr/local/bin/synaps-api-cloudwatch --cloudwatch_listen_port=8777 --logfile=synaps-api-2.log
   root      1012     1  2 15:52 ?        00:09:21 /usr/bin/python /usr/local/bin/synaps-api-cloudwatch --cloudwatch_listen_port=8778 --logfile=synaps-api-3.log
   root      1016     1  1 15:52 ?        00:07:21 /usr/bin/python /usr/local/bin/synaps-api-cloudwatch --cloudwatch_listen_port=8779 --logfile=synaps-api-4.log
   me       17607 13193  0 22:29 pts/14   00:00:00 grep --color=auto synaps-api-cloudwatch

 