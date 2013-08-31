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
  v4 yet. see http://aws.amazon.com/sdkforjava/
  
* Python SDK: Synaps is compatible with AWS SDK for Python, Boto. (tested with 
  ver 2.5.2) see https://github.com/boto/boto

Admin SDK
---------

Synaps has its own SDK which is spined off from AWS SDK for Java (v1.3.12) to 
call admin APIs. If a user who does not have novaadmin role calls Synaps APIs, 
he (or she) will get 400 error message.

Administrators can   

* pass ProjectId parameter for every APIs, so that they can access data in any 
  project.
* put metric data which have their namespace start with reserved word for thier
  services (e.g. "OPENSTACK/" or "SPCS/"). see :ref:`put_metric_data`.
