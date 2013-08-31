.. _build.guide:

Build Guide
===========

You need to build synaps-api and synaps-storm. 

.. code-block:: bash

  git clone https://github.com/spcs/synaps.git
  cd synaps/synaps-api
  python setup.py sdist
  
Then, synaps-yy.mm.xx.tar.gz file can be found under "synaps/synaps-api/dist"
directory.   
  
Next, you should build synaps-storm topology.

.. code-block:: bash

  cd synaps/synaps-storm
  mvn package

Then, synaps-storm-yyyy.mm.xx.jar file could be found under 
"synaps/synaps-storm/target" directory.
