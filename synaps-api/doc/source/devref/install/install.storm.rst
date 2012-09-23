.. _install.storm:

Storm 설치하기
==============

Ubuntu 상에서 Storm 을 설치하고 설정하는 방법에 대해 설명한다. 하나의 nimbus 
노드와 다수의 supervisor 노드에 대해 공통의 설치 작업이 필요하다.

설치
----

.. NOTE::

  :ref:`install.synaps.api` 를 먼저 수행한 뒤 진행해야 한다.
  
  nimbus 노드에서만 apache2 설치 필요
  
  Ubuntu 버전에 따라 JZMQ 설치 방법 다르므로 확인 필요

.. code-block:: bash

  apt-get install openjdk-6-jdk zookeeper make build-essential
  apt-get install uuid-dev unzip pkg-config libtool automake

  # nimbus 노드에서만 apache2 설치
  apt-get install apache2 

  # install zeromq 
  cd ~
  wget http://download.zeromq.org/zeromq-2.1.7.tar.gz
  tar zxvf zeromq-2.1.7.tar.gz
  cd zeromq-2.1.7
  ./configure
  make
  make install
  sudo ldconfig
  easy_install "pyzmq==2.1.7"

  # install storm
  wget https://github.com/downloads/nathanmarz/storm/storm-0.8.0.zip
  mv storm-0.8.0.zip /usr/local/
  cd /usr/local/
  unzip storm-0.8.0
  ln -s /usr/local/storm-0.8.0 storm
  mkdir ~/.storm
  chmod 777 ~/.storm
  ln -s /usr/local/storm/bin/storm /bin/storm
  

  # install JZMQ
  wget https://github.com/nathanmarz/jzmq/tarball/master
  mv master nathanmarz-jzmq-dd3327d.tar.gz
  tar zxvf nathanmarz-jzmq-dd3327d.tar.gz
  cd nathanmarz-jzmq-dd3327d

  # JZMQ for Ubuntu 11.04
  export JAVA_HOME='/usr/lib/jvm/java-6-openjdk'
  ./autogen.sh
  ./configure
  make
  sudo make install

  # JZMQ for Ubuntu 12.04
  export JAVA_HOME='/usr/lib/jvm/java-6-openjdk-amd64'
  ./autogen.sh
  ./configure
  touch src/classdist_noinst.stamp
  cd src/
  CLASSPATH=.:./.:$CLASSPATH javac -d . org/zeromq/ZMQ.java org/zeromq/App.java org/zeromq/ZMQForwarder.java org/zeromq/EmbeddedLibraryTools.java org/zeromq/ZMQQueue.java org/zeromq/ZMQStreamer.java org/zeromq/ZMQException.java
  cd ..
  make
  sudo make install  
  

설정 및 운영
------------

.. NOTE::
  
  구축 환경에 있는 모든 호스트들은 각자의 /etc/hosts 파일에 다른 호스트들의 IP 
  및 HostName 의 정보가 입력되어 있어야만 Storm 이 정상적으로 작동할 수 있다.
  또한, /etc/hosts 파일에서 127.0.0.1 의 HostName 은 아래와 같이 storm 노드의
  호스트네임이 localhost 보다 먼저 위치해야 한다.
  
  .. code-block:: bash
   
   127.0.0.1		mn3 localhost

  
스톰의 각 노드마다 동일하게 주키퍼 설정 파일(/etc/zookeeper/conf/zoo.cfg) 편집

::

   server.1=(HostName):2888:3888
   server.2=(HostName):2889:3889
   server.3=(HostName):2890:3890
   
   ...

.. NOTE::

  (HostName) 에 주키퍼 클러스터를 구성하는 각 노드의 호스트이름을 입력한다.
  
주키퍼 아이디 설정 파일 (/etc/zookeeper/conf/myid) 파일 수정

::

   1

.. NOTE::

  각 노드 별로 zoo.cfg 에 등록한 server.N 에 해당하는 번호를 입력한다.


아래와 같이 Storm 설정파일(/usr/local/storm/conf/storm.yaml) 편집 

.. code-block:: bash

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
   

설정파일을 ~/.storm 디렉토리로 이동

.. code-block:: bash

  cp /usr/local/storm/conf/storm.yaml ~/.storm/
  mkdir /var/lib/dhcp3/
   

LOG 파일 경로의 심볼릭 링크 생성

.. code-block:: bash
  
   rm -rf /usr/local/storm/logs/
   mkdir /var/log/storm
   ln -s /var/log/storm /usr/local/storm/logs 


아래와 같이 주키퍼를 서비스로 등록한다.

.. code-block:: bash

  ln -s /usr/share/zookeeper/bin/zkServer.sh /etc/init.d/


Nimbus, UI 의 역할을 맡는 노드의 경우 OS 시작, 종료 시 서비스 관리가 될 수 
있도록 아래와 같이 적용한다. 

.. code-block:: bash

  sudo update-rc.d zkServer.sh defaluts 80 20  
  sudo update-rc.d storm-nimbus defaluts 81 19
  sudo update-rc.d storm-ui defaluts 82 18
      
Supervisor 의 역할을 맡는 노드의 경우는 아래와 같이 적용한다. 

.. code-block:: bash

  sudo update-rc.d zkServer.sh defaluts 80 20  
  sudo update-rc.d storm-supervisor defaluts 83 17

     
방화벽 설정을 위해 사용하는 포트를 아래와 같이 정리한다. 위 default 설정 및 
새로 설정해준 포트들에 대하여 오픈 필요.

::
 
  2181, 6627, 3772, 3773, 6700, 6701, 6702, 6703, 6704, 6705, 6706, 6707, 2888, 
  2889, 2890, 3888, 3889, 3890
