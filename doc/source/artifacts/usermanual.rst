.. _usermanual:

Synaps SDK User Guide
=====================

Java Example
------------

Put your credentials on SpcsCredentials.properties file. Compile and run the 
code.

.. code-block:: bash
  
  accessKey = your-access-key
  secretKey = your-secret-key

.. code-block:: java

	import java.io.IOException;
	import java.util.ArrayList;
	import java.util.Calendar;
	import java.util.Date;
	
	import com.amazonaws.auth.PropertiesCredentials;
	import com.amazonaws.services.cloudwatch.AmazonCloudWatch;
	import com.amazonaws.services.cloudwatch.AmazonCloudWatchClient;
	import com.amazonaws.services.cloudwatch.model.AlarmHistoryItem;
	import com.amazonaws.services.cloudwatch.model.DescribeAlarmHistoryRequest;
	import com.amazonaws.services.cloudwatch.model.DescribeAlarmHistoryResult;
	import com.amazonaws.services.cloudwatch.model.DescribeAlarmsRequest;
	import com.amazonaws.services.cloudwatch.model.DescribeAlarmsResult;
	import com.amazonaws.services.cloudwatch.model.Dimension;
	import com.amazonaws.services.cloudwatch.model.DimensionFilter;
	import com.amazonaws.services.cloudwatch.model.GetMetricStatisticsRequest;
	import com.amazonaws.services.cloudwatch.model.GetMetricStatisticsResult;
	import com.amazonaws.services.cloudwatch.model.ListMetricsRequest;
	import com.amazonaws.services.cloudwatch.model.ListMetricsResult;
	import com.amazonaws.services.cloudwatch.model.Metric;
	import com.amazonaws.services.cloudwatch.model.MetricAlarm;
	import com.amazonaws.services.cloudwatch.model.MetricDatum;
	import com.amazonaws.services.cloudwatch.model.PutMetricDataRequest;
	
	public class CWSample {
		private AmazonCloudWatch cw;
	
		CWSample() throws IOException {
			cw = new AmazonCloudWatchClient(new PropertiesCredentials(
					CWSample.class.getResourceAsStream("CWSample.properties")));
			cw.setEndpoint("http://synaps.endpoint:3776/monitor/");
		}
	
		void examListMetrics() {
			ListMetricsRequest req = new ListMetricsRequest();
			String nexttoken = null;
			req.setNextToken(nexttoken);
			// req.setMetricName("CPUUtilization");
	
			do {
				req.setNextToken(nexttoken);
				ListMetricsResult ret = cw.listMetrics(req);
				nexttoken = ret.getNextToken();
	
				for (Metric m : ret.getMetrics()) {
					System.out.println("  Metric: " + m);
				}
			} while (nexttoken != null);
		}
	
		void examDescribeAlarms() {
			DescribeAlarmsRequest req = new DescribeAlarmsRequest();
			String nexttoken = null;
			int items_per_page = 100;
	
			req.setMaxRecords(items_per_page);
	
			do {
				req.setNextToken(nexttoken);
				DescribeAlarmsResult ret = cw.describeAlarms(req);
				nexttoken = ret.getNextToken();
				for (MetricAlarm a : ret.getMetricAlarms()) {
					System.out.println("  Alarm: " + a);
				}
			} while (nexttoken != null);
		}
	
		void examPutMetricData() {
			PutMetricDataRequest req = new PutMetricDataRequest();
			ArrayList<Dimension> dimensions1 = new ArrayList<Dimension>();
			ArrayList<Dimension> dimensions2 = new ArrayList<Dimension>();
			Dimension dim1 = new Dimension();
			Dimension dim2 = new Dimension();
			MetricDatum datum1 = new MetricDatum();
			MetricDatum datum2 = new MetricDatum();
			ArrayList<MetricDatum> data = new ArrayList<MetricDatum>();
	
			dim1.setName("instanceId");
			dim1.setValue("instance-00000112");
			dim2.setName("swlbId");
			dim2.setValue("swlb-12345");
	
			dimensions1.add(dim1);
			dimensions2.add(dim2);
	
			datum1.setMetricName("DiskUsage");
			datum1.setValue(10.2);
			datum1.setDimensions(dimensions1);
	
			datum2.setMetricName("RequestsPerSecond");
			datum2.setValue(1000.0);
			datum2.setDimensions(dimensions2);
	
			data.add(datum1);
			data.add(datum2);
	
			req.setMetricData(data);
			req.setNamespace("SYNAPSDEMO/2013");
	
			System.out.println(" PutMetricData Req: " + req);
			cw.putMetricData(req);
		}
	
		void examGetMetricStatistics() {
			GetMetricStatisticsRequest req = new GetMetricStatisticsRequest();
			ArrayList<Dimension> dimensions = new ArrayList<Dimension>();
			Dimension dim = new Dimension();
			ArrayList<String> statistics = new ArrayList<String>();
	
			Calendar startCal = Calendar.getInstance();
			startCal.add(Calendar.DATE, -1);
			Date startTime = startCal.getTime();
	
			Calendar endCal = Calendar.getInstance();
			Date endTime = endCal.getTime();
	
			dim.setName("instanceId");
			dim.setValue("instance-000059b3");
			dimensions.add(dim);
	
			statistics.add("Average");
			statistics.add("Minimum");
			statistics.add("Maximum");
	
			req.setNamespace("SPCS/NOVA");
			req.setMetricName("CPUUtilization");
			req.setDimensions(dimensions);
			req.setStartTime(startTime);
			req.setEndTime(endTime);
			req.setStatistics(statistics);
			req.setPeriod(60);
	
			GetMetricStatisticsResult ret = cw.getMetricStatistics(req);
			System.out.println(ret);
		}
	
		void examPutMetricAlarm() {
		}
	
		void examDescribeAlarmsForMetric() {
	
		}
	
		void examSetAlarmState() {
	
		}
	
		void examDisableAlarmActions() {
	
		}
	
		void examEnableAlarmActions() {
	
		}
	
		void examDescribeAlarmHistory() {
			DescribeAlarmHistoryRequest req = new DescribeAlarmHistoryRequest();
			String nexttoken = null;
	
			req.setMaxRecords(3);
	
			do {
				req.setNextToken(nexttoken);
				DescribeAlarmHistoryResult ret = cw.describeAlarmHistory(req);
				nexttoken = ret.getNextToken();
				for (AlarmHistoryItem h : ret.getAlarmHistoryItems()) {
					System.out.println("  History: " + h);
				}
	
			} while (nexttoken != null);
		}
	
		public static void main(String[] args) throws IOException {
			CWSample cwsample = new CWSample();
	
			cwsample.examListMetrics();
			cwsample.examDescribeAlarms();
			cwsample.examPutMetricData();
			cwsample.examGetMetricStatistics();
			cwsample.examPutMetricAlarm();
			cwsample.examDescribeAlarmsForMetric();
			cwsample.examSetAlarmState();
			cwsample.examDisableAlarmActions();
			cwsample.examEnableAlarmActions();
			cwsample.examDescribeAlarmHistory();
		}
	}
