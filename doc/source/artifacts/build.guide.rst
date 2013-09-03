.. _build.guide:

Build Guide
===========

You need to build synaps-api and synaps-storm. 

.. code-block:: bash

  git clone https://github.com/spcs/synaps.git
  cd synaps
  python setup.py sdist
  
Then, synaps-yy.mm.xx.tar.gz file can be found under "synaps/synaps-api/dist"
directory.   
  
Next, you should build synaps-storm topology.

.. code-block:: bash

  mvn package

Then, synaps-storm-yyyy.mm.xx.jar file could be found under 
"synaps/target" directory.

To build synaps document,

.. code-block:: bash

  python setup.py build_sphinx

Document locations are "build/sphinx/html", "build/sphinx/latex".
If you want to build pdf document, you need to install texlive-full and ko.tex

.. code-block:: bash

  sudo apt-get install texlive-full ko.tex
  cd build/sphinx/latex
  make all-pdf
