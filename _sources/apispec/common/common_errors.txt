.. _common_errors:

공통 에러
=========

모든 API에서 사용하는 공통 에러를 정리함.   

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1
   
   * - 에러
     - 설명
     - HTTP Status Code
   * - InvalidSignature
     - 요청의 서명이 유효하지 않음
     - 400
   * - InvalidRequest
     - 요청이 유효하지 않음
     - 400
   * - InternalFailure
     - 요청이 알 수 없는 에러나 예외 사항, 장애에 의해 실패함
     - 500
          