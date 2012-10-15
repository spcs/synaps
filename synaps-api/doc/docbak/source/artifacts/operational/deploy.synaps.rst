.. _deploy.synaps:

synaps-api, synaps-noti, synaps-storm 배포 
``````````````````````````````````````````

synaps-api, synaps-noti 배포
----------------------------

synaps-api 를 SPCS Synaps 저장소에서 다운받아 아래와 같이 설치한다.

.. code-block:: bash

  wget http://182.194.3.195:8080/synaps-package/product/synaps-yy.mm.dd.tar.gz 
  tar xvfz synaps-yy.mm.dd.tar.gz
  cd synaps-yy.mm.dd
  sudo python setup.py install
  
synaps-storm 배포
-----------------

synaps-nimbus 노드에서 다음과 같이 synaps-storm 을 내려받아 아래와 같이 
실행하면 synaps-supervisor 에 자동으로 코드가 배포되고 실행된다. 

.. code-block:: bash

  wget http://182.194.3.195:8080/synaps-package/product/synaps-storm-yy.mm.dd.jar
  storm jar synaps-storm-yy.mm.dd.jar com.spcs.synaps.PutMetricTopology synapsstorm
