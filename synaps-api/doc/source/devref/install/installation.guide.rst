설치 매뉴얼
===========

본 문서에서는 Ubuntu 환경에서 서비스를 위해 synaps를 각각의 클러스터에 설치하는 
방법을 설명한다. 

.. NOTE::
 
  본 문서에서 설치 작업은 root 권한을 가지고 있는 사용자 환경에서 진행하는 
  것으로 가정한다.


Synaps 는 아래 그림과 같이 구성된다.
 
.. image:: /images/synaps-deployment.jpg
   :width: 100%

#. DB Cluster (cassandraNN) - :ref:`install.cassandra`
#. MQ Cluster (mqNN) - :ref:`install.rabbitmq`
#. API Cluster (synaps-apiNN) - :ref:`install.synaps.api`
#. STORM Cluster (synaps-nimbus, synaps-sypervisorNN) - :ref:`install.storm`
#. synaps-noti Node (synaps-noti) - :ref:`install.synaps.api`


.. toctree::
    :maxdepth: 2

    install.cassandra 
    install.rabbitmq 
    install.storm 
    install.synaps.api
    install.ganglia
    install.common
