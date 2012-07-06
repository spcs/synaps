.. _example:

User SDK 사용 예제
==================

Synaps SDK 예제 사용방법
------------------------
1. SPCS 홈페이지에서 “Synaps-SDK-Sample.zip” 다운로드한다.

2. Eclipse 에서 Import > Existing Projects into Workspace 로 Project를 생성한다.

3. Java Build Path > Libraries 에서 “Add Externel JARs” 버튼을 클릭하여 아래 
   항목의 jar 파일을 지정한다. 

* aws-java-sdk-1.3.10.jar
* commons-codec-1.6.jar
* commons-logging-1.1.1.jar
* fluent-hc-4.2.jar
* httpclient-4.2.jar
* httpclient-cache-4.2.jar
* httpcore-4.2.jar
* httpmime-4.2.jar

4. “AwsCredentials.properties” 파일에 계정정보를 입력한다.

  .. code-block:: bash
  
    accessKey = df6ad231-23f9-4622-810c-acd6ae3e9e67
    secretKey = c142f025-aa84-4cc3-a97e-12bf86c561dc

5. Synaps_Sample.java 에서 Endpoint를 설정한다.

  .. code-block:: java

    cw.setEndpoint("http://182.194.1.163:8773/monitor/");

6. Synaps_Sample.java에서 테스트하고 싶은 API의 주석을 제거하고 파일 실행

7. 정상적으로 실행되면 API 사용예제와 Amazon CloudWatch 설명서를 참고하여 
   개발진행

Synaps SDK 계정접속방법
-----------------------
"AwsCredentials.properties" 정보로 계정접속

"setEndpoint" 함수로 EndPoint 설정

  .. code-block:: java

     AmazonCloudWatch cw = new AmazonCloudWatchClient(
       new PropertiesCredentials(
         Synaps_Sample.class.getResourceAsStream("AwsCredentials.properties")
       )
     );
     cw.setEndpoint("http://182.194.1.163:8773/monitor/");

Action별 SDK 사용 예제
----------------------
  
DeleteAlarms Action
~~~~~~~~~~~~~~~~~~~
"AlarmName" 이라는 이름을 갖는 알람을 삭제하는 예제

  .. code-block:: java

     DeleteAlarmsRequest DAR = new DeleteAlarmsRequest();
     ArrayList<String> DARList = new ArrayList<String>();
     DARList.add("AlarmName");
     DAR.setAlarmNames(DARList);
     cw.deleteAlarms(DAR);

* API reference :ref:`delete_alarms`
* SDK reference `DeleteAlarms`_     
   
DescribeAlarmHistory Action
~~~~~~~~~~~~~~~~~~~~~~~~~~~
프로젝트의 모든 알람 히스토리를 조회하는 예제

  .. code-block:: java

     DescribeAlarmHistoryResult DAHR = cw.describeAlarmHistory();
     System.out.println(DAHR);

* API reference :ref:`describe_alarm_history`
* SDK reference `DescribeAlarmHistory`_     

   
`DescribeAlarms`_
~~~~~~~~~~~~~~~~~
모든 또는 특정 알람에 대한 모든 정보리스트를 반환한다. 

  .. code-block:: java

     DescribeAlarmsResult DAR = cw.describeAlarms();
     System.out.println(DAR);

* API reference :ref:`describe_alarm_history`
* SDK reference `DescribeAlarmHistory`_     
   
`DescribeAlarmsForMetric`_
~~~~~~~~~~~~~~~~~~~~~~~~~~
특정 Metric 에 대한 모든 알람정보를 반환한다. 

  .. code-block:: java

     DescribeAlarmsForMetricRequest DAFMR = new DescribeAlarmsForMetricRequest();
     DAFMR.setMetricName("MetricName");
     DAFMR.setNamespace("NameSpace");
     DescribeAlarmsForMetricResult DAR = cw.describeAlarmsForMetric(DAFMR);
     System.out.println(DAR.getMetricAlarms());
   
`DisableAlarmActions`_
~~~~~~~~~~~~~~~~~~~~~~
TBD
   
`EnableAlarmActions`_ 
~~~~~~~~~~~~~~~~~~~~~
TBD

   
`PutMetricAlarm`_ 
~~~~~~~~~~~~~~~~~

  .. code-block:: java

     PutMetricAlarmRequest PMAR = new PutMetricAlarmRequest();
     PMAR.setAlarmName("AlarmName");
     PMAR.setComparisonOperator("GreaterThanThreshold");
     PMAR.setEvaluationPeriods(10);
     PMAR.setMetricName("MetricName");
     PMAR.setNamespace("NameSpace");
     PMAR.setPeriod(60);
     PMAR.setStatistic("SampleCount");
     PMAR.setThreshold(300.0);
     cw.putMetricAlarm(PMAR);
   
`ListMetrics`_
~~~~~~~~~~~~~~ 

  .. code-block:: java

     ListMetricsRequest LM = new ListMetricsRequest();
     ListMetricsResult LMR = cw.listMetrics(LM);
     System.out.println(LMR.getMetrics());
   
`PutMetricData`_ 
~~~~~~~~~~~~~~~~
"MetricName"이라는 Metric을 특정시간(2012년 6월 28일 14시 ~ 17시)동안 매초마다 
일정값(30)을 입력하는 예제

  .. code-block:: java

	 Dimension dm = new Dimension();
	 dm.setName("DName");
	 dm.setValue("DValue");
	 ArrayList<Dimension> dm_list = new ArrayList<Dimension>();
	 dm_list.add(dm);
	 double value = 0;
	 for(int k=9;k<13;k++){
	   for(int i=0;i<60;i++){
	 	  //create MetricDatum
	 	  MetricDatum MDT = new MetricDatum();
	 	  MDT.setMetricName("MetricName");
	 	  MDT.setDimensions(dm_list);
	 	  value = 30;
	 	  MDT.setValue(value);
	 	  MDT.setUnit("Count");
	 	  @SuppressWarnings("deprecation")
 		  Date InputTime = new Date(112,5,28,5+k,i);
 		  MDT.setTimestamp(InputTime);
 		  System.out.println("Data Input Time : " + InputTime + ", value :" + value);
 	      
 		  //create MetricDatum List
 		  ArrayList<MetricDatum> MDT_list = new ArrayList<MetricDatum>();
 		  MDT_list.add(MDT);
 	   
 		  //create PutMetricDataRequest
 		  PutMetricDataRequest PDR = new PutMetricDataRequest();
 		  PDR.setMetricData(MDT_list);
 		  PDR.setNamespace("NameSpace");
 	   
 		  //execute putMetricData
 		  cw.putMetricData(PDR);	
	   }
	 }
   
`GetMetricStatistics`_
~~~~~~~~~~~~~~~~~~~~~~

특정시간(2012년 6월 28일 14시 ~ 17시) 동안의 통계 값을 조회하는 예제. 

  .. code-block:: java

	 //create Dimension
	 Dimension dm = new Dimension();
	 dm.setName("DName");
	 dm.setValue("DValue");
	 ArrayList<Dimension> dm_list = new ArrayList<Dimension>();
	 dm_list.add(dm); 

	 //create GetMetricStatisticsRequest
	 GetMetricStatisticsRequest MSR = new GetMetricStatisticsRequest();
	 MSR.setDimensions(dm_list);
	 @SuppressWarnings("deprecation")
	 Date StartTime = new Date(112,5,28,14,00);
	 MSR.setStartTime(StartTime);
	 System.out.println("Start Time : " + StartTime);
	 @SuppressWarnings("deprecation")
	 Date EndTime = new Date(112,5,28,17,00);
	 MSR.setEndTime(EndTime);
	 System.out.println("End Time : " + EndTime);
	 MSR.setMetricName("MetricName");
	 MSR.setNamespace("NameSpace");
	 MSR.setPeriod(60);
	 MSR.setUnit("Count");
	 ArrayList<String> Stat = new ArrayList<String>();
	 Stat.add(0, "SampleCount");
	 Stat.add(1, "Sum");
	 Stat.add(2, "Average");
	 Stat.add(3, "Maximum");
	 Stat.add(4, "Minimum");
	 MSR.setStatistics(Stat);
 
	 //create GetMetricStatisticsResult
	 GetMetricStatisticsResult GS = cw.getMetricStatistics(MSR);
	 System.out.println(GS.getLabel());
	 System.out.println(GS.getDatapoints());
   
`SetAlarmState`_
~~~~~~~~~~~~~~~~
TBD


Synaps SDK API 응용예제
------------------------
ListMetrics() 에서 출력된 Metric 중에 아래의 특정 Metric 에 대한 통계정보를 
출력한다.

  .. code-block:: java

    NameSpace: SPCS/NOVA
    MetricName: CPUUtilization
    Dimension: instanceId / instance-0000000f
    Unit: Percent
    Statistics: SampleCount, Average, Maximum, Minimum
    Start Time: 2012년 7월 5일 10시
    End Time: 2012년 7월 5일 11시
    Period: 180초(통계단위)


  .. code-block:: java

	//create Dimension
	Dimension dm = new Dimension();
	dm.setName("instanceId");
	dm.setValue("instance-0000000f");
	ArrayList<Dimension> dm_list = new ArrayList<Dimension>();
	dm_list.add(dm); 
	
	//create GetMetricStatisticsRequest
	GetMetricStatisticsRequest MSR = new GetMetricStatisticsRequest();
	MSR.setDimensions(dm_list);
	@SuppressWarnings("deprecation")
	Date StartTime = new Date(112,6,5,10,00);
	MSR.setStartTime(StartTime);
	@SuppressWarnings("deprecation")
	Date EndTime = new Date(112,6,5,11,00);
	MSR.setEndTime(EndTime);
	MSR.setMetricName("CPUUtilization");
	MSR.setNamespace("SPCS/NOVA");
	MSR.setPeriod(180);
	MSR.setUnit("Percent");
	ArrayList<String> Stat = new ArrayList<String>();
	Stat.add("SampleCount");
	Stat.add("Average");
	Stat.add("Maximum");
	Stat.add("Minimum");
	MSR.setStatistics(Stat);
	  
	//create GetMetricStatisticsResult
	GetMetricStatisticsResult GS = cw.getMetricStatistics(MSR);
	System.out.println(GS.getLabel());
	System.out.println(GS.getDatapoints());

  .. code-block:: java
  
	CPUUtilization
	[{Timestamp: Thu Jul 05 10:00:00 KST 2012, SampleCount: 4.0, 
	  Average: 0.180585700935, Minimum: 0.175029014291, 
	  Maximum: 0.183364138812, Unit: Percent, }, 
	 {Timestamp: Thu Jul 05 10:01:00 KST 2012, SampleCount: 3.0, 
	  Average: 0.175029103639, Minimum: 0.166694235063, 
	  Maximum: 0.183364061564, Unit: Percent, }, 
	 {Timestamp: Thu Jul 05 10:02:00 KST 2012, SampleCount: 3.0, 
	  Average: 0.175029257371, Minimum: 0.166694235063, 
	  Maximum: 0.183364061564, Unit: Percent, }, 
	 {Timestamp: Thu Jul 05 10:03:00 KST 2012, SampleCount: 2.0, 
	  Average: 0.170861855275, Minimum: 0.166694235063, 
	  Maximum: 0.175029475487, Unit: Percent, }, 
	 {Timestamp: Thu Jul 05 10:04:00 KST 2012, SampleCount: 1.0, 
	  Average: 0.175029475487, Minimum: 0.175029475487, 
	  Maximum: 0.175029475487, Unit: Percent, }, 
	 {Timestamp: Thu Jul 05 10:05:00 KST 2012, SampleCount: 0.0, Unit: Count, }, 
	 {Timestamp: Thu Jul 05 10:06:00 KST 2012, SampleCount: 1.0, 
	  Average: 0.197889178604, Minimum: 0.197889178604, 
	  Maximum: 0.197889178604, Unit: Percent, }, ... ]
										
.. _`DeleteAlarms`: http://docs.amazonwebservices.com/AmazonCloudWatch/latest/APIReference/API_DeleteAlarms.html
.. _`DescribeAlarmHistory`: http://docs.amazonwebservices.com/AmazonCloudWatch/latest/APIReference/API_DescribeAlarmHistory.html
.. _`DescribeAlarms`: http://docs.amazonwebservices.com/AmazonCloudWatch/latest/APIReference/API_DescribeAlarms.html
.. _`DescribeAlarmsForMetric`: http://docs.amazonwebservices.com/AmazonCloudWatch/latest/APIReference/API_DescribeAlarmsForMetric.html
.. _`DisableAlarmActions`: http://docs.amazonwebservices.com/AmazonCloudWatch/latest/APIReference/API_DisableAlarmActions.html
.. _`SetAlarmState`: http://docs.amazonwebservices.com/AmazonCloudWatch/latest/APIReference/API_SetAlarmState.html
.. _`GetMetricStatistics`: http://docs.amazonwebservices.com/AmazonCloudWatch/latest/APIReference/API_GetMetricStatistics.html
.. _`EnableAlarmActions`: http://docs.amazonwebservices.com/AmazonCloudWatch/latest/APIReference/API_EnableAlarmActions.html
.. _`PutMetricAlarm`: http://docs.amazonwebservices.com/AmazonCloudWatch/latest/APIReference/API_PutMetricAlarm.html
.. _`ListMetrics`: http://docs.amazonwebservices.com/AmazonCloudWatch/latest/APIReference/API_ListMetrics.html
.. _`PutMetricData`: http://docs.amazonwebservices.com/AmazonCloudWatch/latest/APIReference/API_PutMetricData.html