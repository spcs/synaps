.. _common_query_parameters:

공통 쿼리 매개변수
==================
모든 액션에서 사용하는 매개변수의 목록.  

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - 매개변수 이름
     - 설명
     - 필수 여부
   * - Action
     - 수행할 액션

       기본 값: None

       자료 형: String
     - Yes
   * - AuthParams
     - 질의 요청을 인증하기 위한 매개변수.

       다음을 포함:

       AWSAccessKeyID

       SignatureVersion

       Timestamp

       Signature

       기본 값: None
     - 조건부
   * - AWSAccessKeyId
     - 요청에 서명할 AWS Secrete Access Key 와 짝을 이루는 Access Key ID

       기본 값: None

       자료 형: String
     - Yes
   * - Expires
     - 요청 서명의 만기 일시. ISO 8601 표준에 명기된 대로 YYYY-MM-DDThh:mm:ssZ
       의 형식을 따른다.

       조건: 요청은 Timestamp 또는 Expires 둘 중 하나를 반드시 포함해야 하며,
       모두 포함할 수 없다.

       기본 값: None

       자료 형: String
     - 조건부
   * - Signature
     - 요청 시 생성하는 전자 서명. 

       기본 값: None

       자료 형: String
     - Yes
   * - SignatureMethod
     - 서명에 사용하는 해시 알고리즘

       기본 값: None

       유효 값: HmacSHA256 | HmacSHA1.

       자료 형: String
     - Yes
   * - SignatureVersion
     - 요청에 서명할 때 사용한 서명의 버전

       기본 값: None

       자료 형: String
     - Yes
   * - Timestamp
     - 요청에 서명하는 날짜 및 시간, ISO 8601 표준에 따라 YYYY-MM-DDThh:mm:ssZ 
       와 같은 형식을 따른다.

       조건: 요청은 Timestamp 또는 Expires 둘 중 하나를 반드시 포함해야 하며,
       모두 포함할 수 없다.

       기본 값: None

       자료 형: String
     - 조건부
   * - Version
     - 사용할 API 버전, YYYY-MM-DD.

       기본 값: None

       자료 형: String
     - Yes