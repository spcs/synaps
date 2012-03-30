How to install Synaps-api on Ubuntu 11.04
=========================================

Make sure that you have all dependent packages installed:

.. code-block:: bash

  $ sudo apt-get install build-essential python-dev
  $ sudo apt-get install python-setuptools python-eventlet python-pastedeploy python-webob
  $ sudo apt-get install git

Install thrift

.. code-block:: bash

  $ wget http://pypi.python.org/packages/source/t/thrift/thrift-0.8.0.tar.gz
  $ tar xvfz thrift-0.8.0.tar.gz
  $ cd thrift-0.8.0
  $ sudo python setup.py install
  $ cd ..

Install pycassa

.. code-block:: bash

  $ wget https://github.com/downloads/pycassa/pycassa/pycassa-1.5.1.tar.gz
  $ tar xvfz pycassa-1.5.1.tar.gz
  $ cd pycassa-1.5.1
  $ sudo python setup.py install
  $ cd ..

You can now install synaps-api system-wide:

.. code-block:: bash

  $ git clone ssh://git@redmine.dev/home/git/synaps-api -b master
  $ cd synaps-api
  $ sudo python setup.py install
  $ cd ..

Configure and initial setup synaps-api:

.. code-block:: bash

  $ sudo mkdir /etc/synaps
  $ sudo mkdir /var/log/synaps
  $ sudo cp etc/synaps/* /etc/synaps
  $ sudo vi /etc/synaps/synaps.conf  
  $ sudo synaps-db-initialsetup
