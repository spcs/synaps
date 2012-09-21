.. _install.rabbitmq:

RabbitMQ 설치하기
=================

설치
----

본 문서에서는 기본적인 설치 방법만 가이드 한다. 보다 자세한 설치 및 설정관련
정보는 RabbitMQ 홈페이지를 참조하기를 권장한다.

.. NOTE::

  rabbitmq의 version은 2.8.2 버전 이상을 사용하여야, 이중화 구축이 가능.

아래와 같이 rabbitmq 를 다운받아 설치한다.

.. code-block:: bash

  dpkg -i rabbitmq-server_2.8.2-1_all.deb

설정
----

아래와 같이 설정파일(/etc/rabbitmq/rabbitmq.config)을 수정한다. 아래 설정 
파일에서 synaps-mq01, synaps-mq02 를 클러스터링 되어있는 실제 호스트이름으로 
반영한다. 

::

  [{rabbit, [{cluster_nodes, ['rabbit@synaps-mq01', 'rabbit@synaps-mq02']}]}].

운영
----

RabbitMQ 실행 및 중지

.. code-block:: bash

  rabbitmq-server -detached

.. code-block:: bash

  rabbitmqctl stop


RabbitMQ database 삭제

.. code-block:: bash

  rm -rf /var/lib/rabbitmq/mnesia


erlang.cookie 파일 동기화 ::

  한 노드의 /var/lib/rabbitmq/.erlang.cookie 파일을 다른 노드에 overwrite


클러스터 구성 현황 확인

.. code-block:: bash

  rabbitmqctl cluster_status

  Cluster status of node 'rabbit@synaps-mq02' ...
  [{nodes,[{disc,['rabbit@(RabbitMQ1_HostName)','rabbit@synaps-mq01']}]},
  {running_nodes,['rabbit@(RabbitMQ2_HostName)','rabbit@synaps-mq02']}]
  ...done.
