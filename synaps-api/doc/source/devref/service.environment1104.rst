.. _service.environment1104:

서비스 환경 구축하기
====================

본 문서에서는 Ubuntu 환경에서 서비스를 위해 synaps를 각각의 클러스터에 설치하는 방법을 설명한다. 
synaps 는 다음과 같이 다섯가지 클러스터 그룹으로 구성된다.

#. synaps-전체Node 공통모듈  -  ntp, Ganglia
#. synaps-api - 사용자와 연동하는 웹서비스
#. synaps-mq - 메시지큐 (synaps-api 와 synaps-storm 간의 메시지 전달)
#. synaps-storm - 실시간 분산 처리
#. synaps-database - 카산드라 데이터베이스
#. synaps-mail - Mail 및 SMS 서버

.. image:: /images/synaps-deployment.jpg
   :width: 100%

.. DANGER::
 
 본 문서의 설치 작업은 root 권한을 가지고 있는 사용자 환경에서 
 진행하는 것으로 가정한다.
 

synaps-api 클러스터 구축
------------------------
:ref:`install.synaps.api` 를 참고하여 각각의 웹서버 노드를 구축하고
로드밸런서를 두어 synaps-api 클러스터를 구축한다.


synaps-전체Node 공통모듈 설정
------------------------

* ntp 설치

  .. code-block:: bash
  
   $ apt-get install ntp
   
   
* ntp clinet 설정 

  .. code-block:: bash
  
   $ vi /etc/ntpd.conf
   
   
  ::
  
   # /etc/ntp.conf, configuration for ntpd; see ntp.conf(5) for help
   driftfile /var/lib/ntp/ntp.drift

   # Use Ubuntu's ntp server as a fallback.
   server (NTP_Hostname)

   # Local users may interrogate the ntp server more closely.
   restrict 127.0.0.1

   
  .. DANGER::
  
   ntp를 사용하기 위해서는 udp 123포트 오픈 필요.   
   

synaps-mq 구축 및 이중화 구성
-----------------------------

rabbit mq 2중화 구성

1. 필요조건

* rabbit mq 설치


  .. DANGER::
  
   rabbitmq의 version은 2.8.2 버전 이상을 사용하여야, 이중화 구축이 가능.


  .. code-block:: bash

   $ dpkg -i rabbitmq-server_2.8.2-1_all.deb


* rabbit mq 중지

  .. code-block:: bash

   $ rabbitmqctl stop


* rabbit mq database 삭제

  .. code-block:: bash

   $ rm -rf /var/lib/rabbitmq/mnesia


* erlang.cookie 파일 동기화 ::

   한 노드의 /var/lib/rabbitmq/.erlang.cookie 파일을 다른 노드에 overwrite


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
   [{nodes,[{disc,['rabbit@(RabbitMQ1_HostName)','rabbit@synaps-mq01']}]},
   {running_nodes,['rabbit@(RabbitMQ2_HostName)','rabbit@synaps-mq02']}]
   ...done.

* 부팅 시 Rabbit mq 자동 실행 설정

  .. code-block:: bash

   $ vi /etc/init.d/rc.local
  
   파일의 제일 아래에 다음의 내용 추가.
  
   rabbitmq-server -detached   


synaps-storm 클러스터 구축
--------------------------

 .. DANGER::
  
  구축 환경에 있는 모든 호스트들은 각자의 /etc/hosts 파일에 다른 호스트들의 IP 
  및 HostName 의 정보가 입력되어 있어야만 Storm이 정상적으로 작동할 수 있다.
  또한, /etc/hosts 파일에서 127.0.0.1 의 HostName 은 아래와 같이 localhost 가 
  가장 마지막에 위치하여야 한다.
  
  .. code-block:: bash
   
   127.0.0.1		mn3 localhost
 
 
1. 공통모듈 설치(구축 전 synaps-api 설치 진행)

  .. code-block:: bash

   $ apt-get install openjdk-6-jdk
   $ apt-get install maven2

2. zookeeper 설치

  .. code-block:: bash

   $ apt-get install zookeeper


3. 클러스링을 위한 zookeeper 설정

  .. code-block:: bash

   $ vi /etc/zookeeper/conf/zoo.cfg


* 아래 내용을 수정 ::

   server.1=(HostName):2888:3888
   server.2=(HostName):2889:3889
   server.3=(HostName):2890:3890

* zookeeper id파일 설정(위 설정파일에서 설정한 server.x의 x부분을 각 서버에 넣어줌, server.1은 1만 넣어주면 됨)

  .. code-block:: bash

   $ vi /etc/zookeeper/conf/myid


* server.1의 경우 다음과 같이 수정 ::

   1


4. zookeeper 실행

  .. code-block:: bash

   $ /usr/share/zookeeper/bin/zkServer.sh start
   

* 실행이 되지 않고, cygpath(cywin)관련 오류가 나면 다음의 라인을 찾아 주석처리 ::

   ZOOCFG=`cygpath -wp "$ZOOCFG"`


5. 부팅 시 zookeeper 자동 실행 설정

* rc.local 설정파일 설정 

  .. code-block:: bash

   $ vi /etc/init.d/rc.local


* 파일의 제일 아래에 다음의 내용 추가 ::

   /usr/share/zookeeper/bin/zkServer.sh start


5. zeromq 설치

  .. DANGER::
  
   ZMQ의 version은 반드시 2.1.7을 사용.


  .. code-block:: bash

   $ apt-get install make
   $ apt-get install build-essential
   $ apt-get install uuid-dev
   $ cd ~
   $ wget http://download.zeromq.org/zeromq-2.1.7.tar.gz
   $ tar zxvf zeromq-2.1.7.tar.gz
   $ cd zeromq-2.1.7
   $ ./configure
   $ make
   $ make install
   $ sudo ldconfig


6. jzmq 설치

  .. code-block:: bash

   $ apt-get install pkg-config
   $ apt-get install libtool
   $ apt-get install automake
   $ export JAVA_HOME='/usr/lib/jvm/java-6-openjdk'
   $ cd ~
   $ tar zxvf nathanmarz-jzmq-dd3327d.tar.gz
   $ cd nathanmarz-jzmq-dd3327d
   $ ./autogen.sh
   $ ./configure
   $ make
   $ sudo make install


7. storm 설치

* storm package 다운로드 및 배치 ::

   https://github.com/downloads/nathanmarz/storm/storm-0.8.0.zip


  .. code-block:: bash

   $ apt-get install unzip
   $ mv storm-0.8.0.zip /usr/local/
   $ cd /usr/local/
   $ unzip storm-0.8.0
   $ ln -s /usr/local/storm-0.8.0 storm
   $ mkdir ~/.storm
   $ chmod 777 ~/.storm
   $ ln -s /usr/local/storm/bin/storm /bin/storm


8. storm 설정

* storm 설정파일 설정 

  .. code-block:: bash

   $ vi /usr/local/storm/conf/storm.yaml


* 다음을 설정 파일에 추가 ::

   storm.zookeeper.servers:
        - "(Storm_Nimbus_HostName)" 
        - "(Storm_Supervisor_HostName)" 
        - "(Storm_Supervisor_HostName)" 

   nimbus.host: "(Storm_Nimbus_HostName)" 

   java.library.path: "/usr/lib/jvm/java-6-openjdk-amd64:/usr/local/lib:/opt/local/lib:/usr/lib"
   
   supervisor.slots.ports:
     - 6700
     - 6701
     - 6702
     - 6703
     - 6704
     - 6705
     - 6706
     - 6707
    

* 설정파일을 옮김

  .. code-block:: bash

   $ cp /usr/local/storm/conf/storm.yaml ~/.storm/
   $ mkdir /var/lib/dhcp3/
   

* log 파일 경로의 심볼릭 링크 생성

  .. code-block:: bash
  
   $ rm -rf /usr/local/storm/logs/
   $ mkdir /var/log/storm
   $ ln -s /var/log/storm /usr/local/storm/logs 
   

9. storm 실행

* storm nimbus 머신 실행(at Nimbus)

  .. code-block:: bash

   $ nohup storm nimbus &


* storm supervisor 실행(at Supervisor)

  .. code-block:: bash

   $ nohup storm supervisor &


* storm ui 실행(apache2 package 필요, 필요시 apt-get install apache2 실행, (at Nimbus))

  .. code-block:: bash

   $ nohup storm ui &

   
10. 방화벽 설정

* 사용하는 포트 ::

   2181, 6627, 3772, 3773, 6700, 6701, 6702, 6703, 6704, 6705, 6706, 6707, 2888, 2889, 2890, 3888, 3889, 3890

  위 default 설정 및 새로 설정해준 포트들에 대하여 오픈필요.


11. storm build 및 실행

* storm build

  TBD
   

* storm run(At nimbus)

  .. code-block:: bash

   $ cd ~/synaps/synaps-storm/target
   $ storm jar synaps-storm-2012.##.##.jar com.spcs.synaps.PutMetricTopology metric#####
   
   
* storm run 확인(At supervisor)

  .. code-block:: bash

   $ ps aux | grep python
   
   
* 다음 프로세스 동작 확인(At supervisor)::

   

12. 부팅 시 Storm 자동 실행 설정

* rc.local 설정파일 설정 

  .. code-block:: bash

   $ vi /etc/init.d/rc.local


* Nimbus, UI 의 역할을 맡는 호스트의 경우 파일의 제일 아래에 다음의 내용 추가 ::

   nohup storm nimbus &
   nohup storm ui &
      
* Supervisor 의 역할을 맡는 호스트의 경우 파일의 제일 아래에 다음의 내용 추가 ::
   
   nohup storm supervisor &


synaps-database 클러스터 구축
-----------------------------

1. Cassandra 설치

* 다운로드 및 압축풀기

  .. code-block:: bash
  
   $ cd ~
   $ tar zxvf apache-cassandra-1.0.8-bin.tar.gz /usr/local/


* 클러스터 설정

  .. code-block:: bash

   $ vi /usr/local/apache-cassandra-1.0.8/conf/cassandra.yaml


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
             - seeds: "(Cassandra_HostName1),(Cassandra_HostName2),(Cassandra_HostName3)"

   # Setting this to 0.0.0.0 is always wrong.
   listen_address: (Local_HostName)

   rpc_address: 0.0.0.0
   

* Cassandra 실행 ::

   /usr/local/apache-cassandra-1.0.8/bin/cassandra


3. 부팅 시 Cassandra 자동 실행 설정

* rc.local 설정파일 설정 

  .. code-block:: bash

   $ vi /etc/init.d/rc.local


* 파일의 제일 아래에 다음의 내용 추가 ::

   /usr/local/apache-cassandra-1.0.8/bin/cassandra

   
   
synaps-noti 구축
----------------

1. 공통모듈 설치(구축 전 synaps-api 설치 진행)

  .. code-block:: bash

   $ apt-get install python-mysqldb
   $ apt-get install python-zmq
   
   
2. SMSMMSAgent 설치

* 사용 패키지 설치

  .. code-block:: bash

   $ apt-get install mysql-server
   $ apt-get install ksh
   $ apt-get install openjdk-6-jdk
   

* database 생성

  .. code-block:: bash

   $ mysql -u root -psynaps
   mysql> create database synaps;
   mysql> exit
   

* SMSMMSAgent 설치

  .. code-block:: bash
  
   $ cd ~
   $ tar zxvf SMSMMSAgent.tar.gz
   $ mv SMSMMSAgent /usr/local/
   

* SMSMMSAgent 설정

  .. code-block:: bash

   $ vi /usr/local/SMSMMSAgent/conf/vega.cfg
   
   
  .. code-block:: bash
   
    SMS_SVC=ON
    MMS_SVC=OFF
    ADMIN_PORT=6271
    
    # MySQL
    DB_DRIVER=com.mysql.jdbc.Driver
    DB_URL=jdbc:mysql://localhost/synaps
    DB_ID=root
    DB_PWD=synaps
    
    HOME_DIR=../
    LOG_DIR=../log/

    CONVERT_CHAR=N
    FROM_CHAR=ISO8859_1
    TO_CHAR=KSC5601
    
    XFIELDS=
    XSCHEMA=
    
    SMS_ONLY_SEND=N

    SMS_IP=210.94.53.49
    SMS_PORT=9000

    #########################
    SMS_DELIVER_CNT=1

    SMS_DELIVER_ID_1=ossweb
    SMS_DELIVER_PWD_1=oss0919
    SMS_DELIVER_MAX_1=3

    SMS_DEFAULT_DELIVER_ID=ossweb

    SMS_REPORT_ID=ossweb
    SMS_REPORT_PWD=oss0919
    #########################

    SMS_SEND=SMS_SEND
    SMS_RESULT=SMS_RESULT
    SMS_SPAM=SMS_SPAM
    SMS_RESULT_DIV=N

    SMS_TTL_SEND=180

    SMS_BAN_TIME=0~0

    SMS_DUP_CHK=N

    SMS_ENCRYPT=N
    
    MMS_ONLY_SEND=N

    MMS_DELIVER_IP=210.118.51.150
    MMS_DELIVER_PORT=7000

    MMS_REPORT_IP=210.118.51.150
    MMS_REPORT_PORT=7003

    MMS_DELIVER_CNT=1
    MMS_DELIVER_ID_1=ossweb
    MMS_DELIVER_PWD_1=oss0919
    MMS_DELIVER_MAX_1=3
    MMS_REPORT_ID=ossweb
    MMS_REPORT_PWD=oss0919
    
    MMS_DEFAULT_DELIVER_ID=ossweb
    
    MMS_SEND=MMS_SEND
    MMS_SEND_CONTENTS=MMS_SEND_CONTENTS
    MMS_SEND_BROADCAST=MMS_SEND_BROADCAST
    MMS_RESULT=MMS_RESULT
    MMS_RESULT_CONTENTS=MMS_RESULT_CONTENTS
    MMS_SPAM=MMS_SPAM

    MMS_RESULT_DIV=N

    MMS_TTL_SEND=180

    MMS_BAN_TIME=0~0

    MMS_DUP_CHK=N

    MMS_FAIL_SMS_SEND=N

    MMS_FAIL_SMS_SEND_TTL=24

    MMS_FAIL_SMS_SEND_ERR=2103,4305,2300,2506

    MMS_FAIL_SMS_DELIVER_ID=

    MMS_FAIL_RESEND_TIME=0~0

    MMS_FAIL_SCHED_TIME=0
    

* table 생성
다음 sql문을 이용하여 table 생성

  ::
   
   CREATE TABLE `SMS_RESULT` (
   `msg_key` varchar(20) NOT NULL DEFAULT '',
   `evnt_sqc` decimal(5,0) NOT NULL,
   `receiver` varchar(20) NOT NULL,
   `sender` varchar(20) DEFAULT NULL,
   `message` varchar(100) DEFAULT NULL,
   `url` varchar(100) DEFAULT NULL,
   `depart` varchar(10) DEFAULT NULL,
   `extend` varchar(5) DEFAULT NULL,
   `reg_time` varchar(14) DEFAULT NULL,
   `reserve_time` varchar(14) DEFAULT NULL,
   `nat_code` int(3) DEFAULT NULL,
   `fixed_com` varchar(4) DEFAULT NULL,
   `tran_id` varchar(20) DEFAULT NULL,
   `submit_result` char(3) DEFAULT NULL,
   `submit_time` varchar(14) DEFAULT NULL,
   `deliver_time` varchar(14) DEFAULT NULL,
   `report_time` varchar(14) DEFAULT NULL,
   `result` char(3) DEFAULT NULL,
   `result_desc` varchar(20) DEFAULT NULL,
   `mms_msg_key` varchar(20) DEFAULT NULL,
   `dest` varchar(5) DEFAULT NULL,
   PRIMARY KEY (`msg_key`)
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
   
   CREATE TABLE `SMS_SEND` (
   `msg_key` varchar(20) NOT NULL DEFAULT '',
   `receiver` varchar(20) NOT NULL,
   `sender` varchar(20) DEFAULT NULL,
   `message` varchar(100) NOT NULL,
   `url` varchar(100) DEFAULT NULL,
   `depart` varchar(10) DEFAULT NULL,
   `extend` varchar(5) DEFAULT NULL,
   `reg_time` varchar(14) NOT NULL,
   `reserve_time` varchar(14) NOT NULL DEFAULT '00000000000000',
   `nat_code` int(3) DEFAULT NULL,
   `fixed_com` varchar(4) DEFAULT NULL,
   `tran_id` varchar(20) NOT NULL DEFAULT ' ',
   `mms_msg_key` varchar(20) DEFAULT NULL,
   PRIMARY KEY (`msg_key`)
   )ENGINE=InnoDB DEFAULT CHARSET=utf8;
   
   CREATE TABLE `SMS_SPAM` (
   `seq` int(8) NOT NULL,
   `tran_id` varchar(20) NOT NULL DEFAULT 'ALL',
   `reg_time` varchar(14) NOT NULL,
   `receiver` varchar(20) NOT NULL,
   `remark` varchar(100) DEFAULT NULL,
   PRIMARY KEY (`seq`)
   ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
   
   
3. SMSMMSAgent 실행

* SMSMMSAgent 실행 방법

  .. code-block:: bash

   $ /usr/local/SMSMMSAgent/bin/tagent_start.sh
   $ synaps-notification
   

4. 부팅 시 SMSMMSAgent 자동 실행 설정

* rc.local 설정파일 설정 

  .. code-block:: bash

   $ vi /etc/init.d/rc.local


* 파일의 제일 아래에 다음의 내용 추가 ::

   /usr/local/SMSMMSAgent/bin/tagent_start.sh
   synaps-notification
 
 
  