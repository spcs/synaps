.. _install.synaps.api:

synaps-api 설치하기
===================

Ubuntu(11.04)상에서 synaps-api를 설치 및 설정 방법에 대해 설명한다.


의존모듈 설치
`````````````

기본 패키지 설치
----------------

.. code-block:: bash

  $ sudo apt-get install build-essential python-dev
  $ sudo apt-get install python-setuptools python-eventlet python-pastedeploy python-webob
  $ sudo apt-get install git

thrift 설치
-----------
카산드라를 사용하기 위해서 thrift 의 파이썬 모듈을 설치한다.

.. code-block:: bash

  $ wget http://pypi.python.org/packages/source/t/thrift/thrift-0.8.0.tar.gz
  $ tar xvfz thrift-0.8.0.tar.gz
  $ cd thrift-0.8.0
  $ sudo python setup.py install
  $ cd ..
  
  
pycassa 설치
-------------
카산드라 파이썬 클라이언트(pycassa)를 설치한다.

.. code-block:: bash

  $ wget https://github.com/downloads/pycassa/pycassa/pycassa-1.5.1.tar.gz
  $ tar xvfz pycassa-1.5.1.tar.gz
  $ cd pycassa-1.5.1
  $ sudo python setup.py install
  $ cd ..
  
pika 설치
---------
python RabbitMQ 클라이언트인 pika를 설치한다.

  
synaps 설치
```````````
synaps-api 설치 및 설정
-----------------------
아래와 같이 synaps 프로젝트를 clone 해서 synaps-api를 설치한다.

.. code-block:: bash

  $ git clone ssh://git@redmine.dev/home/git/synaps -b master
  $ cd synaps/synaps-api
  $ sudo python setup.py install
  $ cd ..
  
/etc/synaps/synaps.conf 에서 환경에 맞는 설정을 적용한다.

.. code-block:: bash

  $ sudo mkdir /etc/synaps
  $ sudo mkdir /var/log/synaps
  $ sudo cp etc/synaps/* /etc/synaps
  $ sudo vi /etc/synaps/synaps.conf  

synaps-database 초기화
----------------------
데이터베이스에 keyspace 및 column family 가 정의되지 않은 경우, 아래 명령을 
통해 데이터베이스의 초기 셋업을 수행한다. 

.. code-block:: bash

  $ sudo synaps-db-initialsetup

.. DANGER::
  위 명령이 무엇을 하는지 정확히 파악한 후 실행할 것. /etc/synaps/synaps.conf에 
  설정된 DB의 키스페이스를 drop 시킨후 키스페이스 및 컬럼패밀리를 재생성함. 
  실수로 실행한 경우, 모든 데이터를 유실하게 됨.

synaps-api 실행
---------------
아래와 같이 synaps-api 를 실행시킬 수 있다. 로그는 /var/log/synaps 에 위치한다.

.. code-block:: bash

  $ sudo /etc/init.d/synaps-api start
