.. _development.environment:

로컬 개발 환경 구축하기
=======================

Ubuntu 상에서 SPCS Synaps를 개발하기 위한 환경을 구축하는 방법을 설명한다. 
본 지침에서 독자는 이미 GIT 에 익숙하다고 가정한다.

환경 구성하기 
`````````````

카산드라 데이터베이스 설치
--------------------------
synaps는 metric 통계자료 및 alarm 을 저장하기 위해서 카산드라를 사용한다. 
로컬 개발 환경을 구축하기 위해서 카산드라를 설치해야한다. 카산드라를 설치하는 
여러 방법 중 `Debian 패키지를 통한 설치`_ 를 권장한다. 현재 synaps는 
카산드라 1.0.8 에서 개발 중이다.

.. _`Debian 패키지를 통한 설치`: http://wiki.apache.org/cassandra/DebianPackaging

Storm 설치
----------
synaps는 metric의 스트림을 실시간으로 모니터하기 위해서 실시간 분산 처리 엔진인
Storm_ 을 사용한다. `Storm의 개발환경 설정에 관련한 문서`_ 를 참고해서 Storm을 
설치한다.

.. _Storm: https://github.com/nathanmarz/storm/wiki
.. _`Storm의 개발환경 설정에 관련한 문서`: https://github.com/nathanmarz/storm/wiki/Setting-up-development-environment    
 
RabbitMQ 설치
-------------
synaps는 웹서버에서 Storm으로 메시지를 넘겨주기 위해 RabbitMQ_ 를 사용한다. 
`데비안 설치문서`_ 를 참고해서 RabbitMQ를 설치한다.

.. _RabbitMQ: http://www.rabbitmq.com/
.. _`데비안 설치문서`: http://www.rabbitmq.com/install-debian.html

synaps-api 빌드, 설치 및 실행
------------------------------
:ref:`install.synaps.api` 참고

synaps-storm 빌드 및 실행
-------------------------
TBD