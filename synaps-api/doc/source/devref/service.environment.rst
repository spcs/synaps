.. _service.environment:

서비스 환경 구축하기
====================

본 문서에서는 서비스를 위해 synaps를 각각의 클러스터에 설치하는 방법을 설명한다. 
synaps 는 다음과 같이 네가지 클러스터 그룹으로 구성된다.

#. synaps-api - 사용자와 연동하는 웹서비스
#. synaps-mq - 메시지큐 (synaps-api 와 synaps-storm 간의 메시지 전달)
#. synaps-storm - 실시간 분산 처리
#. synaps-database - 카산드라 데이터베이스

.. image:: /images/synaps-deployment.jpg
   :width: 100%

synaps-api 클러스터 구축
------------------------
:ref:`install.synaps.api` 를 참고하여 각각의 웹서버 노드를 구축하고
로드밸런서를 두어 synaps-api 클러스터를 구축한다.


synaps-mq 구축 및 이중화 구성
------------------------------------------

rabbit mq 2중화 구성

1. 필요조건

* rabbit mq 설치

  .. code-block:: bash

   $ dpkg -i rabbitmq-server_2.8.2-1_all.deb


* rabbit mq 중지

  .. code-block:: bash

   $ rabbitmqctl stop


* rabbit mq database 삭제

  .. code-block:: bash

   $ rm -rf /var/lib/rabbitmq/mnesia


* erlang_cookie 파일 동기화 ::

   한 노드의 /var/lib/rabbitmq/.erlang_cookie 파일을 다른 노드에 overwrite


2. 클러스터링

* 클러스터링 정보 설정

  .. code-block:: bash

   $ vi /etc/rabbitmq/rabbitmq.config


* 아래 내용 저장 ::

   [{rabbit, [{cluster_nodes, ['rabbit@synaps-mq01', 'rabbit@synaps-mq02']}]}].


* Rabbit mq 실행

  .. code-block:: bash

   $ rabbitmq-server -detached


* 이중화 확인

  .. code-block:: bash

   $ rabbitmqctl cluster_status


  ::

   Cluster status of node 'rabbit@synaps-mq02' ...
   [{nodes,[{disc,['rabbit@rabbit@synaps-mq02','rabbit@rabbit@synaps-mq01']}]},
   {running_nodes,['rabbit@rabbit@synaps-mq01','rabbit@rabbit@synaps-mq02']}]
   ...done.

synaps-storm 클러스터 구축
--------------------------
1. 공통모듈 설치

  .. code-block:: bash

   $ apt-get install openjdk-6-jdk


2. zookeeper 설치

  .. code-block:: bash

   $ apt-get install zookeeper


3. 클러스링을 위한 zookeeper 설정

  .. code-block:: bash

   $ vi /etc/zookeeper/conf/zoo.cfg


* 아래 내용을 수정 ::

   server.1=10.101.1.217:2888:3888
   server.2=10.101.1.113:2889:3889
   server.3=10.101.1.207:2890:3890

* zookeeper id파일 설정(위 설정파일에서 설정한 server.x의 x부분을 각 서버에 넣어줌, server.1은 1만 넣어주면 됨)

  .. code-block:: bash

   $ vi /etc/zookeeper/conf/myid


* 다음과 같이 수정 ::

   1


4. zookeeper 실행

  .. code-block:: bash

   $ /usr/share/zookeeper/bin/zkServer.sh start


* 실행이 되지 않고, cygpath(cywin)관련 오류가 나면 다음의 라인을 찾아 주석처리 ::

   *ZOOCFG=`cygpath -wp "$ZOOCFG"`


5. zeromq 설치

  .. code-block:: bash

   $ apt-get install make
   $ apt-get install build-essential
   $ apt-get install uuid-dev
   $ tar zxvf zeromq-2.1.11.tar.gz
   $ cd zeromq-2.1.11
   $ ./configure
   $ make install
   $ sudo ldconfig


6. jzmq 설치

  .. code-block:: bash

   $ apt-get install pkg-config
   $ apt-get install libtool
   $ apt-get install automake
   $ export JAVA_HOME='/usr/lib/jvm/java-6-openjdk'
   $ ./autogen.sh
   $ ./configure
   $ make
   $ sudo make install


7. storm 설치

* storm package 다운로드 및 배치 ::

   https://github.com/downloads/nathanmarz/storm/storm-0.7.1.zip


  .. code-block:: bash

   $ apt-get install unzip
   $ mkdir ~/opt
   $ mv storm-0.7.1.zip ~/opt/
   $ cd ~/opt
   $ unzip storm-0.7.1
   $ ln -s ~/opt/storm-0.7.1 storm
   $ mkdir ~/.storm
   $ chmod 777 ~/.storm


8. storm 설정

* storm 설정파일 설정 

  .. code-block:: bash

   $ vi stormdirectory/conf/storm.yaml


* 다음을 수정 ::

   storm.zookeeper.servers:
        - "10.101.1.113" 
        - "10.101.1.207" 
        - "10.101.1.217" 

   nimbus.host: "10.101.1.217" 

   java.library.path: "/usr/lib/jvm/java-6-openjdk:/usr/local/lib:/opt/local/lib:/usr/lib" 

* 설정파일을 옮김

  .. code-block::bash

   $ cp storm/conf/storm.yaml ~/.storm/
   $ mkdir /var/lib/dhcp3/


9. storm 실행

* storm nimbus 머신 실행(at Nimbus)

  .. code-block:: bash

   $ bin/storm nimbus


* storm supervisor 실행(at Supervisor)

  .. code-block:: bash

   $ bin/storm supervisor


* storm ui 실행(apache2 package 필요, 필요시 apt-get install apache2 실행, (at Nimbus))

  .. code-block:: bash

   $ bin/storm ui


10. 방화벽 설정

* 사용하는 포트 ::

   2181, 6627, 3772, 3773, 6700, 6701, 6702, 6703, 2888, 2889, 2890, 3888, 3889, 3890

위 default 설정 및 새로 설정해준 포트들에 대하여 오픈필요.

synaps-database 클러스터 구축
-----------------------------
1. SPCS내의 VM에 디스크 마운트

* SPCS 내의 VM에 디스크 마운트

  .. code-block:: bash

   $ fdisk /dev/vdb


* 이후 아래 순서로 진행 ::

   n -> p -> 1 -> 1-> enter -> w


* 마운트할 디렉토리 생성

  .. code-block:: bash

   $ mkdir /cassDATA


* ext3 형식으로 디스크 포맷

  .. code-block:: bash

   $ mke2fs -j /dev/vdb


* 생성한 디렉토리에 디스크 마운트

  .. code-block:: bash

   $ mount -t ext3 /dev/vdb /cassDATA


* fstab에 마운트 옵션 추가

  .. code-block:: bash

   $ vi /etc/fstab


* 맨 아랫줄에 아래 내용 추가 ::

   /dev/vdb	/cassDATA	ext3	defaults	1	2


2. Cassandra 설치

* 다운로드 및 압축풀기

  .. code-block:: bash

   $ tar zxvf apache-cassandra-1.0.8-bin.tar.gz


* 클러스터 설정

  .. code-block:: bash

   $ vi apache-cassandra-1.0.8/conf/cassandra.yaml


* 아래 내용 찾아서 수정 ::

   cluster_name: 'Synaps Product Cluster'

   # directories where Cassandra should store data on disk.
   data_file_directories:
       - /cassDATA/data

   # commit log
   commitlog_directory: /cassDATA/commitlog

   # saved caches
   saved_caches_directory: /cassDATA/saved_caches

   seed_provider:
       # Addresses of hosts that are deemed contact points.
       # Cassandra nodes use this list of hosts to find each other and learn
       # the topology of the ring.  You must change this if you are running
       # multiple nodes!
       - class_name: org.apache.cassandra.locator.SimpleSeedProvider
         parameters:
             # seeds is actually a comma-delimited list of addresses.
             # Ex: "<ip1>,<ip2>,<ip3>"
             - seeds: "10.101.0.165,10.101.2.108,10.101.1.198"

   # Setting this to 0.0.0.0 is always wrong.
   listen_address: 10.101.2.67

   rpc_address: 0.0.0.0


* 방화벽 설정 ::

   카산드라 사용 포트 : 7000, 7001, 9160


pandas 설치(web server, storm server)
--------------------------------------------------

1. 필요 패키지 설치

* numpy 설치

  .. code-block:: bash

   $ apt-get install python-numpy
   
* python-dateutil 설치

  .. code-block:: bash

   $ wget http://labix.org/download/python-dateutil/python-dateutil-1.5.tar.gz
   $ tar zxvf python-dateutil-1.5.tar.gz
   $ python setup.py install
   
2. pandas 설치

* pandas 설치

  .. code-block:: bash

   $ wget http://pypi.python.org/packages/source/p/pandas/pandas-0.7.3.tar.gz#md5=e4876ea5882accce15f6f37750f3ffec
   $ tar zxvf pandas-0.7.3.tar.gz
   $ python setup.py install