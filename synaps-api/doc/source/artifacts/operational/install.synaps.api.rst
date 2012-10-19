.. _install.synaps.api.ubuntu:

Install synaps-api and synaps-noti
==================================

This document describes how to install synaps-api and synaps-noti on the 
Ubuntu machine.

 
Pre-installation requirements
-----------------------------

.. code-block:: bash

   # install apt packages
   sudo apt-get install build-essential python-dev memcached
   sudo apt-get install python-setuptools python-eventlet python-pastedeploy 
   sudo apt-get install git python-gflags python-netaddr python-memcache
   sudo apt-get install python-numpy python-webob python-ldap
   
   # synaps-noti 사용하는 경우
   sudo apt-get install python-mysqldb python-zmq
   
   # download 3rd-party packages
   mkdir /tmp/packages
   cd /tmp/packages
   wget http://labix.org/download/python-dateutil/python-dateutil-1.5.tar.gz
   wget http://pypi.python.org/packages/source/p/pandas/pandas-0.7.3.tar.gz#md5=e4876ea5882accce15f6f37750f3ffec
   wget http://pypi.python.org/packages/source/t/thrift/thrift-0.8.0.tar.gz
   wget https://github.com/downloads/pycassa/pycassa/pycassa-1.5.1.tar.gz
   wget http://pypi.python.org/packages/source/p/pika/pika-0.9.5.tar.gz
   wget http://boto.googlecode.com/files/boto-2.5.2.tar.gz
   
   # unzip packages
   tar xvfz python-dateutil-1.5.tar.gz
   tar xvfz pandas-0.7.3.tar.gz
   tar xvfz thrift-0.8.0.tar.gz
   tar xvfz pycassa-1.5.1.tar.gz
   tar xvfz pika-0.9.5.tar.gz
   tar xvfz boto-2.5.2.tar.gz
   
   # install python-dateutil 1.5
   cd python-dateutil-1.5
   sudo python setup.py install
   cd ..   

   # install pandas 0.7.3
   cd pandas-0.7.3/
   sudo python setup.py install
   cd ..
   
   # install thrift
   cd thrift-0.8.0
   sudo python setup.py install
   cd ..
   
   # install pycassa
   cd pycassa-1.5.1
   sudo python setup.py install
   cd ..
  
   # install pika  
   cd pika-0.9.5
   sudo python setup.py install
   cd ..

   # install boto  
   cd boto-2.5.2
   sudo python setup.py install
   cd ..
  
  
Install synaps-api
------------------

Clone synaps source code from Github.

.. code-block:: bash

  git clone https://github.com/spcs/synaps.git
  cd synaps/synaps-api
  sudo python setup.py install
