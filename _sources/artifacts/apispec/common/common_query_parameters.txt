.. _common_query_parameters:

Common Qurey Parameters
=======================

It describes common query parameters for all API actions.

.. list-table:: 
   :widths: 20 50 10
   :header-rows: 1

   * - Name
     - Description
     - Mandatory
   * - Action
     - Action to execute

       Default Value: None

       Data Type: String
     - Yes
   * - AuthParams
     - 질의 요청을 인증하기 위한 매개변수.

       This includes the following:

       AWSAccessKeyID

       SignatureVersion

       Timestamp

       Signature

       Default Value: None
     - 조건부
   * - AWSAccessKeyId
     - 요청에 서명할 AWS Secrete Access Key 와 짝을 이루는 Access Key ID

       Default Value: None

       Data Type: String
     - Yes
   * - Expires
     - 요청 서명의 만기 일시. ISO 8601 표준에 명기된 대로 YYYY-MM-DDThh:mm:ssZ
       의 형식을 따른다.

       조건: 요청은 Timestamp 또는 Expires 둘 중 하나를 반드시 포함해야 하며,
       모두 포함할 수 없다.

       Default Value: None

       Data Type: String
     - 조건부
   * - Signature
     - 요청 시 생성하는 전자 서명. 

       Default Value: None

       Data Type: String
     - Yes
   * - SignatureMethod
     - 서명에 사용하는 해시 알고리즘

       Default Value: None

       유효 값: HmacSHA256 | HmacSHA1.

       Data Type: String
     - Yes
   * - SignatureVersion
     - 요청에 서명할 때 사용한 서명의 버전

       Default Value: None

       Data Type: String
     - Yes
   * - Timestamp
     - 요청에 서명하는 날짜 및 시간, ISO 8601 표준에 따라 YYYY-MM-DDThh:mm:ssZ 
       와 같은 형식을 따른다.

       조건: 요청은 Timestamp 또는 Expires 둘 중 하나를 반드시 포함해야 하며,
       모두 포함할 수 없다.

       Default Value: None

       Data Type: String
     - 조건부
   * - Version
     - 사용할 API 버전, YYYY-MM-DD.

       Default Value: None

       Data Type: String
     - Yes