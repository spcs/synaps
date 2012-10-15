..
      Copyright 2012 Samsung SDS.
      All Rights Reserved.


SDK(Software Development Toolkit) specification
===============================================

Synaps SDK의 사용자는 일반 사용자(User)와 관리자(Admin)으로 구분된다. 

User SDK
--------
SPCS Synaps는 AWS CloudWatch와 호환되며 아래의 CloudWatch용 사용자 SDK와 
호환되며 별도의 SPCS 전용 User SDK를 제공하지는 않는다.

endpoint를 AWS CloudWatch가 아닌 SPCS Synaps 의 endpoint로 설정하고 인증을 위한 
ACCESS_KEY 와 ACCESS_SECRET_KEY 를 SPCS 사용자 계정의 정보로 설정하여 사용한다.  

Java SDK
++++++++

Java용 AWS SDK 와 호환된다. (ver 1.3.12 로 테스트)

* http://aws.amazon.com/ko/sdkforjava/ 참고
  
Python SDK
++++++++++
AWS 연동용 Python 패키지인 Boto와 호환된다. (ver 2.5.2 로 테스트)

* http://boto.cloudhackers.com/en/latest/index.html 참고


Admin SDK
---------
SPCS의 프로덕트간 연동을 위해 Synaps Admin SDK를 사용한다. SPCS Admin 권한이 
있는 계정의 ACCESS_KEY 와 ACCESS_SECRET_KEY 정보를 설정하고 사용한다.  

User SDK와의 차이점

* 각 액션마다 ProjectId 입력 가능
* :ref:`put_metric_data` 수행 시, "SPCS/" 로 시작하는 namespace 를 갖는 메트릭 
  데이터 입력 가능

Java SDK
++++++++
Java용 AWS SDK의 spin-off 를 통해 연동한다. 

* SDK는 담당자에게 문의

SDK User Guide
--------------

.. toctree::
    :maxdepth: 2

    sdk/user.sdk.example.rst
