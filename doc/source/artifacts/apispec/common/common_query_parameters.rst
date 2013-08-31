.. _common_query_parameters:

Common Query Parameters
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
     - Parameters for authentication to query request.

       This includes the following:

       AWSAccessKeyID

       SignatureVersion

       Timestamp

       Signature

       Default Value: None
     - Conditional
   * - AWSAccessKeyId
     - Access key which makes a pair with AWS Secrete Access Key to signature 
       for request.

       Default Value: None

       Data Type: String
     - Yes
   * - Expires
     - Expire date and time for request. Follow the ISO 8601 standard; such as
       YYYY-MM-DDThh:mm:ssZ

       Condition: Request must has Timestamp or Expires, not allow both.

       Default Value: None

       Data Type: String
     - Conditional
   * - Signature
     - Electronic signature that is generated when it is requested.

       Default Value: None

       Data Type: String
     - Yes
   * - SignatureMethod
     - Hash algorithm to use for signature.

       Default Value: None

       Valid value: HmacSHA256 | HmacSHA1.

       Data Type: String
     - Yes
   * - SignatureVersion
     - used Signature's version when sign for request.

       Default Value: None

       Data Type: String
     - Yes
   * - Timestamp
     - date and time for sign a request. Follow the ISO 8601 standard; such as
       YYYY-MM-DDThh:mm:ssZ

       Condition: Request must has Timestamp or Expires, not allow both.

       Default Value: None

       Data Type: String
     - Conditional
   * - Version
     - API's version, such as YYYY-MM-DD.

       Default Value: None

       Data Type: String
     - Yes