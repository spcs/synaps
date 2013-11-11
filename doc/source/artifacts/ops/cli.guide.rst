..
      Copyright 2012, 2013 Samsung SDS.
      All Rights Reserved.


Command line interface Guide
============================

There are two kind of CLI tools for Synaps. Those are AWS CLI and cwutil of 
boto. 


AWS CLI
-------

Using AWS CLI is a good way to manage service.

You need to install AWS CLI and setup your credentials in the config file.

to install AWS CLI,

.. code-block:: bash

	$ pip install awscli
  
Configuration file path is ~/.aws/config. It looks like below.

.. code-block:: none

	[default]
	aws_access_key_id = ACCESS-KEY
	aws_secret_access_key = SECRET-KEY
	region = us-east-1


Usage example,

.. code-block:: bash

	$ aws --endpoint-url http://synaps.service.url:3776/monitor cloudwatch list-metrics

For more details, see http://docs.aws.amazon.com/cli/latest/userguide


cwutil(boto) Guide
------------------

Using cwutil in the boto, you can also manage service. Use spcs branch of boto.
which is added more CLI functions based on the original cwutil of boto.

to install cwutil(spcs branch),

.. code-block:: bash

	$ pip install https://github.com/spcs/boto/archive/2.9.9.spcs.tar.gz 
 
Usage example,

To list metrics.

.. code-block:: bash

	$ cwutil ls
	
To list metrics in SPCS/SYNAPS namespace.

.. code-block:: bash

	$ cwutil ls SPCS/SYNAPS

cwutil's usage is,

.. code-block:: none

	Usage: cwutil [command]
		delete_alarm - 
	    Delete Alarm
	    
		disable_alarm_actions - 
	    Enable alarm actions.
	        alarmName: Alarm name to activate action.
	    
		enable_alarm_actions - 
	    Enable alarm actions.
	        alarmName: Alarm name to activate action.
	    
		help - 
	    Print help message, optionally about a specific function
	    
		history - 
	    List alarm history
	    
	    Action
	    
		ls - 
	    List metrics, optionally filtering by a specific namespace
	        namespace: Optional Namespace to filter on
	    
		ls_alarm - 
	    Describe list of alarms.
	    
		put - 
	    Publish custom metrics
	        namespace: The namespace to use; values starting with "AWS/" are reserved
	        metric_name: The name of the metric to update
	        dimensions: The dimensions to use, formatted as Name:Value (such as QueueName:myQueue)
	        value: The value to store, mutually exclusive with `statistics`
	        statistics: The statistics to store, mutually exclusive with `value`
	            (must specify all of "Minimum", "Maximum", "Sum", "SampleCount")
	        timestamp: The timestamp of this measurement, default is current server time
	        unit: Unit to track, default depends on what metric is being tracked
	    
		put_alarm - 
	    Put MetricAlarm
	        namespace:
	        metric_name:
	        dimensions: 
	        alarm_name: 
	        statistic: default "Average"
	        comparison: default ">" 
	        threshold: default 90
	        unit: default None
	        period: default 60
	        evaluation_periods: default 1 minute
	        description: default None
	        alarm_actions: default None
	        insufficient_data_actions: default None 
	        ok_actions: default None
	    
		stats - 
	    Lists the statistics for a specific metric
	        namespace: The namespace to use, usually "AWS/EC2", "AWS/SQS", etc.
	        metric_name: The name of the metric to track, pulled from `ls`
	        dimensions: The dimensions to use, formatted as Name:Value (such as QueueName:myQueue)
	        statistics: The statistics to measure, defaults to "Average"
	             'Minimum', 'Maximum', 'Sum', 'Average', 'SampleCount'
	        start_time: Start time, default to now - 1 day
	        end_time: End time, default to now
	        period: Period/interval for counts, default to 60 minutes
	        unit: Unit to track, default depends on what metric is being tracked

