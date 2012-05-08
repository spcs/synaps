.. _service.environment:

서비스 환경 구축하기
====================

본 문서에서는 서비스를 위해 synaps를 각각의 클러스터에 설치하는 방법을 설명한다. 
synaps 는 다음과 같이 네가지 클러스터 그룹으로 구성된다.

#. synaps-api - 사용자와 연동하는 웹서비스
#. synaps-mq - 메시지큐 (synaps-api 와 synaps-storm 간의 메시지 전달)
#. synaps-storm - 실시간 분산 처리
#. synaps-database - 카산드라 데이터베이스

synaps-api 클러스터 구축
------------------------
:ref:`install.synaps.api` 를 참고하여 각각의 웹서버 노드를 구축하고
로드밸런서를 두어 synaps-api 클러스터를 구축한다.

TBD

synaps-mq 구축
--------------
TBD

synaps-storm 클러스터 구축
--------------------------
synaps-storm 은 nimbus 노드와 worker 노드로 나뉜다.

TBD

synaps-database 클러스터 구축
-----------------------------
TBD