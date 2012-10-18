.. _install.common:

공통 설치 및 설정
`````````````````

Synaps 설정
-----------
다운 받은 synaps api 패키지에서 설정파일을 복사한다. /etc/synaps/synaps.conf 
에서 환경에 맞는 설정을 적용한다. 설정 파일은 클러스터 내 노드 모두 동일해야 
한다. (synaps-api, synaps-storm, synaps-noti 노드에 해당)

.. code-block:: bash

  sudo mkdir /etc/synaps
  sudo mkdir /var/log/synaps
  sudo cp etc/synaps/api-paste.ini /etc/synaps/api-paste.ini
  sudo cp etc/synaps/synaps.conf /etc/synaps/synaps.conf
  sudo vi /etc/synaps/synaps.conf


Database 초기 셋업
------------------
데이터베이스에 keyspace 및 column family 가 정의되지 않은 경우, 아래 명령을 
통해 데이터베이스의 초기 셋업을 수행한다. (synaps-api 에서 초기 한 번만 수행)

.. code-block:: bash

  sudo synaps-syncdb
  
  
API 실행 및 정지
----------------
아래와 같이 synaps-api 를 실행 및 정지시킬 수 있다. 로그는 /var/log/synaps 에 
위치한다. 

.. code-block:: bash

  sudo /etc/init.d/synaps-api start
  sudo /etc/init.d/synaps-api stop 


OS 설정
-------

운영체제의 최대 open 가능 file 수를 조정한다.

.. code-block:: bash

  ulimit -Hn 65535
  ulimit -Sn 65535
  vi /etc/security/limits.conf
  
파일 하단에 다음의 내용을 추가한다.

.. code-block:: bash
  
  root            hard    nofile          65535
  root            soft    nofile          65535

     
OS 시작 및 종료 시 자동으로 시작, 종료 되도록 rc.d 등록

.. code-block:: bash

  sudo update-rc.d synaps-api defaults 80
  /etc/init.d/synaps-api restart


NTP 설정
--------

ntpd 를 설치하고 NTP Client 설정을 한다.

.. code-block:: bash
  
 apt-get install ntp

아래와 같이 설정파일 /etc/ntpd.conf 를 수정한다.   
   
.. code-block:: bash
  
  # /etc/ntp.conf, configuration for ntpd; see ntp.conf(5) for help
  driftfile /var/lib/ntp/ntp.drift
  # Use Ubuntu's ntp server as a fallback.
  server "ntp host" 
  # Local users may interrogate the ntp server more closely.
  restrict 127.0.0.1
   
.. NOTE::

  위 설정파일의 "ntp host" 대신 NTP 서버의 호스트이름 또는 IP로 서버 
  등록한다. 

.. NOTE::
  
  ntp 를 사용하기 위해서는 udp 123포트 오픈 필요.