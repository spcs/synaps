.. _common_errors:

공통 에러
=========

모든 API에서 사용하는 공통 에러를 정리함.   

.. list-table:: 
   :widths: 15 50 10
   :header-rows: 1

   * - 에러
     - 설명
     - HTTP Status Code
   * - IncompleteSignature
     - The request signature does not conform to AWS standards.
     - 400
   * - InternalFailure
     - The request processing has failed due to some unknown error, exception 
       or failure.
     - 500
   * - InvalidAction
     - The action or operation requested is invalid.
     - 400
   * - InvalidClientTokenId
     - The X.509 certificate or AWS Access Key ID provided does not exist in our 
       records.
     - 403
   * - InvalidParameterCombination
     - Parameters that must not be used together were used together.
     - 400
   * - InvalidParameterValue
     - A bad or out-of-range value was supplied for the input parameter.
     - 400
   * - InvalidQueryParameter
     - AWS query string is malformed, does not adhere to AWS standards.
     - 400
   * - MalformedQueryString
     - The query string is malformed.
     - 404
   * - MissingAction
     - The request is missing an action or operation parameter.
     - 400
   * - MissingAuthenticationToken
     - Request must contain either a valid (registered) AWS Access Key ID.
     - 403
   * - MissingParameter
     - An input parameter that is mandatory for processing the request is not 
       supplied.
     - 400
   * - OptInRequired
     - The AWS Access Key ID needs a subscription for the service.
     - 403
   * - RequestExpired
     - Request is past expires date or the request date (either with 15 minute 
       padding), or the request date occurs more than 15 minutes in the future.
     - 400
   * - ServiceUnavailable
     - The request has failed due to a temporary failure of the server.
     - 503
   * - Throttling
     - Request was denied due to request throttling.
     - 400     