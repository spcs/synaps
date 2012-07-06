.. _user.sdk.rst:

User SDK
========
SPCS Synaps는 AWS CloudWatch와 호환되며 아래의 CloudWatch용 사용자 SDK와 
호환되며 별도의 SPCS 전용 User SDK를 제공하지는 않는다.

endpoint를 AWS CloudWatch가 아닌 SPCS Synaps 의 endpoint로 설정하고 인증을 위한 
ACCESS_KEY 와 ACCESS_SECRET_KEY 를 SPCS 사용자 계정의 정보로 설정하여 사용한다.  

Java SDK
--------
Java용 AWS SDK 와 호환된다. (ver 1.3.12 로 테스트)

* http://aws.amazon.com/ko/sdkforjava/ 참고
  
Python SDK
----------
AWS 연동용 Python 패키지인 Boto와 호환된다. (ver 2.5.2 로 테스트)

* http://boto.cloudhackers.com/en/latest/index.html 참고
