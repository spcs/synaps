.. _usermanual:

Synaps SDK User Guide
=====================

Configure Credentials
---------------------

Put your credentials on SpcsCredentials.properties file.

.. code-block:: bash
  
  accessKey = df6ad231-23f9-4622-810c-acd6ae3e9e67
  secretKey = c142f025-aa84-4cc3-a97e-12bf86c561dc

You can initiate CloudWatch object as below.

.. code-block:: java

   AmazonCloudWatch cw = new AmazonCloudWatchClient(
     new PropertiesCredentials(
       Synaps_Sample.class.getResourceAsStream("SpcsCredentials.properties")
     )
   );
   cw.setEndpoint("http://182.194.1.163:8773/monitor/");


ListMetrics Example
-------------------

Following code is an example for using :ref:`list_metrics`.

.. code-block:: java

  ListMetricsRequest LM = new ListMetricsRequest();
  ListMetricsResult LMR = cw.listMetrics(LM);
  System.out.println(LMR.getMetrics());
     

PutMetricData Example
---------------------

Following code is an example for using :ref:`put_metric_data`.

It puts specific metric data value (30) for every second in a time frame (from 
2012-06-28 14:00 to 17:00).

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

   
GetMetricStatistics Example
---------------------------

Following code is an example for using :ref:`get_metric_statistics`.

It retreives CPUUtilization statistics of instance-0000000f (average, maximum, 
minimum and sample count) in the time frame from 2010-07-05 10:00 to 2010-07-05 
11:00.  


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

The result is described below.

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


DeleteAlarms Example
--------------------

Following code is an example for using :ref:`delete_alarms`.

.. code-block:: java

   DeleteAlarmsRequest DAR = new DeleteAlarmsRequest();
   ArrayList<String> DARList = new ArrayList<String>();
   DARList.add("AlarmName");
   DAR.setAlarmNames(DARList);
   cw.deleteAlarms(DAR);
   
DescribeAlarms Example
----------------------

Following code is an example for using :ref:`describe_alarm_history` 

.. code-block:: java

   DescribeAlarmsResult DAR = cw.describeAlarms();
   System.out.println(DAR);


DescribeAlarmsForMetric Example
-------------------------------

Following code is an example for using :ref:`describe_alarms_for_metric`

.. code-block:: java
   
   DescribeAlarmsForMetricRequest DAFMR = new DescribeAlarmsForMetricRequest();
   DAFMR.setMetricName("MetricName");
   DAFMR.setNamespace("NameSpace");
   DescribeAlarmsForMetricResult DAR = cw.describeAlarmsForMetric(DAFMR);
   System.out.println(DAR.getMetricAlarms());


PutMetricAlarm Example
----------------------

Following code is an example for using :ref:`put_metric_alarm`

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


SetAlarmState Example
---------------------
TBD
   
DisableAlarmActions Example
---------------------------
TBD
   
EnableAlarmActions Example
--------------------------
TBD


DescribeAlarmHistory Example
----------------------------

Following code is an example for using :ref:`describe_alarm_history`

.. code-block:: java

   DescribeAlarmHistoryResult DAHR = cw.describeAlarmHistory();
   System.out.println(DAHR);
