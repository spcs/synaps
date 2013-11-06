.. _developersguide:

Developer's Guide
=================

How to develope and test Synaps
-------------------------------

Set up development environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
see :ref:`general.installation.guide`


Build Synaps
~~~~~~~~~~~~
see :ref:`build.guide`


Run synaps-api
~~~~~~~~~~~~~~

After synaps installation, you can run synaps as below.

.. code-block:: bash
 
  $ sudo synaps-api-cloudwatch

Run synaps-storm (local mode)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After build synaps-storm topology(synaps-storm-yyyy.xx.xx.jar), you can run
the topology on storm local mode as below. (When you don't pass topology name,
it will run on local mode)

.. code-block:: bash
 
  $ sudo storm jar synaps-storm-yyyy.xx.xx.jar 

Run testcase (Functional/Integration test)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now you can run testcase to check your Synaps running OK

.. code-block:: bash

  ~/git/synaps/synaps-api/synaps/tests$ python test_cloudwatch.py

Module Index
============

.. toctree::
    :maxdepth: 1

    ../api/autoindex.rst

