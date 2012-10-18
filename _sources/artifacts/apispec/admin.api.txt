.. _admin_api:

관리자 API 규격
===============
SPCS Synaps 관리자 API는 :ref:`user_api` 의 액션 마다 추가로 ProjectId 
매개변수를 입력받으며 나머지는 :ref:`user_api` 과 동일하다.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - 이름
     - 설명
     - 필수 여부
   * - ProjectId
     - API 액션을 수행할 프로젝트 식별자 

       Type: String
     - No
