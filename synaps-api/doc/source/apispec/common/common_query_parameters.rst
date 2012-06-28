.. _common_query_parameters:

공통 쿼리 매개변수
==================

This section lists the request parameters that all actions use. Any 
action-specific parameters are listed in the topic for the action.  

.. list-table:: 
   :widths: 15 50 10
   :header-rows: 1

   * - Parameter Name
     - 설명
     - 필수 여부
   * - Action
     - The action to perform.

       Default: None

       Type: String
     - Yes
   * - AuthParams
     - The parameters required to authenticate a query request.

       Contains:

       AWSAccessKeyID

       SignatureVersion

       Timestamp

       Signature

       Default: None
     - Conditional
   * - AWSAccessKeyId
     - The Access Key ID corresponding to the AWS Secret Access Key you used to 
       sign the request.

       Default: None

       Type: String
     - Yes
   * - Expires
     - The date and time at which the request signature expires, in the format 
       YYYY-MM-DDThh:mm:ssZ, as specified in the ISO 8601 standard.

       Condition: Requests must include either Timestamp or Expires, but not 
       both.

       Default: None

       Type: String
     - Conditional
   * - SecurityToken
     - The temporary security token obtained through a call to AWS Security 
       Token Service. Only available for actions in the following AWS services: 
       Amazon EC2, Amazon Simple Notification Service, Amazon SQS, and AWS 
       SimpleDB.

       Default: None

       Type: String
     - 
   * - Signature
     - The digital signature you created for the request. Refer to the service's 
       developer documentation for information about how to generate the 
       signature.

       Default: None

       Type: String
     - Yes
   * - SignatureMethod
     - The hash algorithm you used to create the request signature.

       Default: None

       Valid Values: HmacSHA256 | HmacSHA1.

       Type: String
     - Yes
   * - SignatureVersion
     - The signature version you use to sign the request. Set this to the value 
       recommended in your product-specific documentation on security.

       Default: None

       Type: String
     - Yes
   * - Timestamp
     - The date and time the request was signed, in the format 
       YYYY-MM-DDThh:mm:ssZ, as specified in the ISO 8601 standard.

       Condition: Requests must include either Timestamp or Expires, but not 
       both.

       Default: None

       Type: String
     - Conditional
   * - Version
     - The API version to use, in the format YYYY-MM-DD.

       Default: None

       Type: String
     - Yes

.. toctree::
   :maxdepth: 1