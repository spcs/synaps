.. _user_sdk_example:

User SDK guide
==============

Setting credentials
-------------------
1. write your credentials in the SpcsCredentials.properties file.

  .. code-block:: bash
  
    accessKey = df6ad231-23f9-4622-810c-acd6ae3e9e67
    secretKey = c142f025-aa84-4cc3-a97e-12bf86c561dc

2. Initiate an AmazonCloudWatchClient object as below,

  .. code-block:: java

     AmazonCloudWatch cw = new AmazonCloudWatchClient(
       new PropertiesCredentials(
         Synaps_Sample.class.getResourceAsStream("SpcsCredentials.properties")
       )
     );
     cw.setEndpoint("http://182.194.1.163:8773/monitor/");

Examples
--------

ListMetrics
~~~~~~~~~~~

  .. code-block:: java

     ListMetricsRequest LM = new ListMetricsRequest();
     ListMetricsResult LMR = cw.listMetrics(LM);
     System.out.println(LMR.getMetrics());
     
* API reference: :ref:`list_metrics`

PutMetricData
~~~~~~~~~~~~~

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

* API reference: :ref:`put_metric_data`
   
GetMetricStatistics
~~~~~~~~~~~~~~~~~~~

아래 예제에서는 SPCS Nova 의 가상머신 인스턴스 instance-0000000f의 CPU 사용률의
2012년 7월 5일 10시부터 한 시간 동안의 3분(180초) 주기의 평균, 최대, 최소, 샘플 
갯수를 조회한다.

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

위 예제의 실행 결과는 다음과 같다.

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

* API reference: :ref:`get_metric_statistics`

DeleteAlarms
~~~~~~~~~~~~

"AlarmName" 이라는 이름을 갖는 알람을 삭제하는 예제

  .. code-block:: java

     DeleteAlarmsRequest DAR = new DeleteAlarmsRequest();
     ArrayList<String> DARList = new ArrayList<String>();
     DARList.add("AlarmName");
     DAR.setAlarmNames(DARList);
     cw.deleteAlarms(DAR);

* API reference: :ref:`delete_alarms`
   
DescribeAlarms
~~~~~~~~~~~~~~
모든 또는 특정 알람에 대한 모든 정보리스트를 반환한다. 

  .. code-block:: java

     DescribeAlarmsResult DAR = cw.describeAlarms();
     System.out.println(DAR);

* API reference: :ref:`describe_alarm_history`
   
DescribeAlarmsForMetric
~~~~~~~~~~~~~~~~~~~~~~~
특정 Metric 에 대한 모든 알람정보를 반환한다. 

  .. code-block:: java

     DescribeAlarmsForMetricRequest DAFMR = new DescribeAlarmsForMetricRequest();
     DAFMR.setMetricName("MetricName");
     DAFMR.setNamespace("NameSpace");
     DescribeAlarmsForMetricResult DAR = cw.describeAlarmsForMetric(DAFMR);
     System.out.println(DAR.getMetricAlarms());

* API reference: :ref:`describe_alarms_for_metric`
   
PutMetricAlarm
~~~~~~~~~~~~~~

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

* API reference: :ref:`put_metric_alarm`

SetAlarmState
~~~~~~~~~~~~~
TBD
   
DisableAlarmActions
~~~~~~~~~~~~~~~~~~~
TBD
   
EnableAlarmActions
~~~~~~~~~~~~~~~~~~
TBD


DescribeAlarmHistory
~~~~~~~~~~~~~~~~~~~~
프로젝트의 모든 알람 히스토리를 조회하는 예제

  .. code-block:: java

     DescribeAlarmHistoryResult DAHR = cw.describeAlarmHistory();
     System.out.println(DAHR);

* API reference: :ref:`describe_alarm_history`
