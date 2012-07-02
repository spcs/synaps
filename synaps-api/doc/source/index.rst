..
      Copyright 2012 Samsung SDS.
      All Rights Reserved.

SPCS Synaps Documentation
=========================

Overview
--------

SPCS Synaps는 다음과 같은 특징을 갖는 클라우드 컴퓨팅 모니터링 시스템이다.

* **선형 확장성**: 극한의 부하에도 작동할 수 있어야한다.
* **API 호환성**: Synaps는 AWS CloudWatch API와 호환되는 API를 제공한다.
* **실시간 모니터링**: Synaps는 입력되는 메트릭을 실시간으로 모니터링하여 보다 
  정밀한 알람을 제공한다. 

Development Guide
-----------------

.. toctree::
    :maxdepth: 2

    devref/development.environment
    devref/service.environment
    devref/install.synaps.api
	devref/api

Application Programming Interface
---------------------------------

.. toctree::
    :maxdepth: 3

    apispec/index.rst   

Software Development Kit
------------------------

.. toctree::
    :maxdepth: 2
    
    sdk/index.rst
    sdk/example.rst

Module References
-----------------    
.. toctree::
    :maxdepth: 1

    ../api/autoindex

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
