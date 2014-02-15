..
      Copyright 2012 Samsung SDS.
      All Rights Reserved.

SDK(Software Development Toolkit) description
=============================================

Synaps provides following two types of SDK.

User SDK
--------

Synaps provides AWS CloudWatch compatible APIs so that users can use AWS 
CloudWatch SDKs. Synaps does not provide Synaps-specialized SDK for users. 


* Java SDK: Synaps is compatible with AWS SDK for Java (ver 1.3.12). But, it 
  doesn't support more recent version. Synaps does not supports AWS Signature 
  v4 yet. see https://github.com/aws/aws-sdk-java
  
  To use more recent version of AWS SDK for Java, use SPCS branch that 
  works with Signature v2 module. see https://github.com/spcs/aws-sdk-java
  
* Python SDK: Synaps is compatible with AWS SDK for Python, Boto. 
  see https://github.com/boto/boto


Admin SDK
---------

Synaps has its own SDK which is a spin-off of AWS SDK for Java (v1.3.12) to 
call admin APIs. If a user who does not have synapsadmin or novaadmin role 
calls Synaps APIs, he (or she) will get 400 error message. 

Administrators can   

* pass ProjectId parameter for every APIs, so that they can access data in any 
  project.
* put metric data which have their namespace start with reserved word for their
  services (e.g. "OPENSTACK/" or "SPCS/"). see :ref:`put_metric_data`.
* put alarm which have their name start with reserved word for their services.