..
      Copyright 2012 Samsung SDS.
      All Rights Reserved.

SPCS Synaps Documentation
=========================

Overview
--------

SPCS Synaps는 메트릭 데이터를 입력, 감시 및 관리하며 메트릭을 기반으로 알람을 
설정할 수 있는 클라우드 모니터링 시스템이다.

사용자는 사용자 정의 메트릭을 직접 정의해서 입력할 수 있으며, 별도의 메트릭 
정의 없이 SPCS의 제품이 자동으로 입력해주는 기본 메트릭(ex, VM의 CPU 사용률, 
Disk I/O, Network I/O 등)을 사용할 수 있다.

일반적으로 SPCS Synaps는 고객의 애플리케이션과 서비스가 효율적으로 잘 작동하는
상태를 유지할 수 있도록 하는데 사용한다. 예를 들어, 어느 정도의 네트워크 부하
이하에서만 잘 작동하는 웹 서비스를 SPCS에서 구축한 경우, 해당 메트릭에 알람을
설정해두고 임계치가 넘은 경우 전자메일이나 문자메시지를 받아 볼 수 있으며 
(E-mail 및 SMS 기능은 8월 구현 예정), Auto Scaling 서비스와 연동하여 서버를 
추가하거나 줄일 수 있다. (10월 연동 예정)

.. toctree::
    :maxdepth: 3

    intro/concept.rst
    intro/defaultmetrics.rst

설계 결정 사항
--------------
SPCS는 다음과 같은 특징을 갖는다. 

* **선형 확장성**: 극한의 부하에도 작동할 수 있어야한다.
* **API 호환성**: Synaps는 AWS CloudWatch API와 호환되는 API를 제공한다.
* **실시간 모니터링**: Synaps는 입력되는 메트릭을 실시간으로 모니터링하여 보다 
  정밀한 알람을 제공한다. 


Application Programming Interface
---------------------------------
SPCS Synaps API의 사용자는 일반 사용자(User)와 관리자(Admin)으로 구분된다. 

.. toctree::
    :maxdepth: 3

    apispec/user.api.rst   
    apispec/admin.api.rst
    apispec/endpoints.rst

Software Development Kit
------------------------
SPCS Synaps SDK의 사용자는 일반 사용자(User)와 관리자(Admin)으로 구분된다. 

.. toctree::
    :maxdepth: 2
    
    sdk/user.sdk.rst
    sdk/admin.sdk.rst
    sdk/user.sdk.example.rst

Synaps Development Guide
------------------------

.. toctree::
    :maxdepth: 2

    devref/development.environment
    devref/service.environment
    devref/install.synaps.api


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
