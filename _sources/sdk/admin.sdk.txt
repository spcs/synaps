.. _admin.sdk:

Admin SDK
=========
SPCS의 프로덕트간 연동을 위해 Synaps Admin SDK를 사용한다. SPCS Admin 권한이 
있는 계정의 ACCESS_KEY 와 ACCESS_SECRET_KEY 정보를 설정하고 사용한다.  

User SDK와의 차이점

* 각 액션마다 ProjectId 입력 가능
* :ref:`put_metric_data` 수행 시, "SPCS/" 로 시작하는 namespace 를 갖는 메트릭 
  데이터 입력 가능

Java SDK
--------
Java용 AWS SDK의 spin-off 를 통해 연동한다. 

* SDK는 담당자에게 문의
