.. _install.synaps.api:

synaps-api 설치하기
===================

Ubuntu 상에서 synaps-api를 설치 및 설정 방법에 대해 설명한다.

.. DANGER::
 
 본 문서의 설치 작업은 root 권한을 가지고 있는 사용자 환경에서 
 진행하는 것으로 가정한다.
 
 
의존모듈 설치
`````````````

기본 패키지 설치
----------------

.. code-block:: bash

  $ sudo apt-get install build-essential python-dev memcached
  $ sudo apt-get install python-setuptools python-eventlet python-pastedeploy python-webob python-ldap
  $ sudo apt-get install git python-gflags python-netaddr python-memcache


pandas 설치(web server, storm server)
--------------------------------------------------

1. 필요 패키지 설치

* numpy 설치

  .. code-block:: bash

   $ apt-get install python-numpy

   
* python-dateutil 설치

  .. code-block:: bash

   $ cd ~
   $ wget http://labix.org/download/python-dateutil/python-dateutil-1.5.tar.gz
   $ tar zxvf python-dateutil-1.5.tar.gz
   $ cd python-dateutil-1.5
   $ python setup.py install

   
2. pandas 설치

* pandas 설치

  .. code-block:: bash

   $ cd ~   
   $ wget http://pypi.python.org/packages/source/p/pandas/pandas-0.7.3.tar.gz#md5=e4876ea5882accce15f6f37750f3ffec
   $ tar zxvf pandas-0.7.3.tar.gz
   $ cd pandas-0.7.3/
   $ python setup.py install


thrift 설치
-----------
카산드라를 사용하기 위해서 thrift 의 파이썬 모듈을 설치한다.

.. code-block:: bash

  $ cd ~
  $ wget http://pypi.python.org/packages/source/t/thrift/thrift-0.8.0.tar.gz
  $ tar xvfz thrift-0.8.0.tar.gz
  $ cd thrift-0.8.0
  $ sudo python setup.py install
  $ cd ..
  
  
pycassa 설치
-------------
카산드라 파이썬 클라이언트(pycassa)를 설치한다.

.. code-block:: bash

  $ cd ~  
  $ wget https://github.com/downloads/pycassa/pycassa/pycassa-1.5.1.tar.gz
  $ tar xvfz pycassa-1.5.1.tar.gz
  $ cd pycassa-1.5.1
  $ sudo python setup.py install
  
  
pika 설치
---------
python RabbitMQ 클라이언트인 pika를 설치한다.

.. code-block:: bash

  $ cd ~  
  $ wget http://pypi.python.org/packages/source/p/pika/pika-0.9.5.tar.gz
  $ tar xvfz pika-0.9.5.tar.gz
  $ cd pika-0.9.5
  $ sudo python setup.py install
  
  
boto 설치
---------

.. code-block:: bash

  $ cd ~
  $ wget http://boto.googlecode.com/files/boto-2.3.0.tar.gz
  $ tar xvfz boto-2.3.0.tar.gz
  $ cd boto-2.3.0
  $ sudo python setup.py install
  
  
synaps 설치
```````````
synaps-api 설치 및 설정
-----------------------
아래와 같이 synaps 프로젝트를 clone 해서 synaps-api를 설치한다.

.. code-block:: bash

  $ cd ~  
  $ git clone ssh://git@redmine.dev/home/git/synaps -b master
  $ cd synaps/synaps-api
  $ sudo python setup.py install
  
  
/etc/synaps/synaps.conf 에서 환경에 맞는 설정을 적용한다.

.. code-block:: bash

  $ sudo mkdir /etc/synaps
  $ sudo mkdir /var/log/synaps
  $ sudo cp etc/synaps/* /etc/synaps
  $ sudo vi /etc/synaps/synaps.conf


운영체제의 최대 open 가능 file 수를 조정한다.

.. code-block:: bash

  $ ulimit -Hn 65535
  $ ulimit -Sn 65535
  $ vi /etc/security/limits.conf
  
  파일 하단에 다음의 내용을 추가한다.
  
  root            hard    nofile          65535
  root            soft    nofile          65535
     

synaps-database 초기화
----------------------
데이터베이스에 keyspace 및 column family 가 정의되지 않은 경우, 아래 명령을 
통해 데이터베이스의 초기 셋업을 수행한다. 

.. code-block:: bash

  $ sudo synaps-syncdb
  

.. DANGER::
  위 명령이 무엇을 하는지 정확히 파악한 후 실행할 것. /etc/synaps/synaps.conf에 
  설정된 DB의 키스페이스 및 컬럼패밀리의 유무 여부 및 정합성을 체크하고, 
  이에 대해 조치함.
   
  
synaps-api 실행 및 정지
-----------------------
아래와 같이 synaps-api 를 실행 및 정지시킬 수 있다. 로그는 /var/log/synaps 에 
위치한다.

.. code-block:: bash

  $ sudo /etc/init.d/synaps-api start
  $ sudo /etc/init.d/synaps-api stop 


synaps-api 부팅 시 자동 실행
-----------------------
아래와 같이 synaps-api 를 부팅 시 자동으로 실행하게 할 수 있다.

.. code-block:: bash

  $ vi /etc/init.d/rc.local
  
  파일의 제일 아래에 다음의 내용 추가.
  
  /etc/init.d/synaps-api start
  

synaps-api 업그레이드
-----------------------
synaps-api 를 업그레이드 할 경우, 위의 과정을 전부 반복할 필요 없이, 아래와 같이
synaps 프로젝트를 clone 해서 synaps-api를 설치하는 과정만 되풀이하면 된다.

.. code-block:: bash

  $ cd ~  
  $ git clone ssh://git@redmine.dev/home/git/synaps -b master
  $ cd synaps/synaps-api
  $ sudo python setup.py install
  
  
