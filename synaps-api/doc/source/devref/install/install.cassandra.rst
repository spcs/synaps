.. _install.cassandra:

Cassandra 설치하기
``````````````````

본 문서에서는 기본적인 설치 방법만 가이드 한다. 보다 자세한 설치 및 설정관련
정보는 Cassandra 홈페이지를 참조한다.

설치
----

아래와 같이 카산드라를 설치한다.

.. code-block:: bash

  tar xvfz apache-cassandra-1.0.8-bin.tar.gz /usr/local/

설정
----

아래와 같이 설정 파일(/usr/local/apache-cassandra-1.0.8/conf/cassandra.yaml) 편집 

.. NOTE::

  seeds 에 카산드라 노드의 호스트이름 리스트를 등록한다.
  
  listen_address 에 해당 노드의 카산드라 호스트이름을 등록한다. 


::

   cluster_name: 'Synaps Product Cluster'

   # directories where Cassandra should store data on disk.
   data_file_directories:
       - /var/log/cassandra/data

   # commit log
   commitlog_directory: /var/log/cassandra/commitlog

   # saved caches
   saved_caches_directory: /var/log/cassandra/saved_caches

   seed_provider:
       # Addresses of hosts that are deemed contact points.
       # Cassandra nodes use this list of hosts to find each other and learn
       # the topology of the ring.  You must change this if you are running
       # multiple nodes!
       - class_name: org.apache.cassandra.locator.SimpleSeedProvider
         parameters:
             # seeds is actually a comma-delimited list of addresses.
             # Ex: "<ip1>,<ip2>,<ip3>"
             - seeds: "(Cassandra_HostName1),(Cassandra_HostName2),(Cassandra_HostName3)"

   # Setting this to 0.0.0.0 is always wrong.
   listen_address: (Local_HostName)

   rpc_address: 0.0.0.0
