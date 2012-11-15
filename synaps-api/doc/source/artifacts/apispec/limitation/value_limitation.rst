.. _value_limitation:

Value limitation
======================

This page describes length and type limitation of parameters in Synaps.  

Parameters
-------------

.. list-table:: 
   :widths: 30 15 15 40
   :header-rows: 1

   * - Name
     - Data type
     - Length limitation
     - Valid value / Type limitation
   * - ActionPrefix
     - String
     - 1 ~ 1024      
     - Value consisting of only numbers can not be used.
   * - ActionEnabled
     - Boolean
     - 
     - 
   * - AlarmActions
     - String list
     - 
     - 
   * - AlarmArn
     - String
     - 1 ~ 1000  
     - 
   * - AlarmConfigurationUpdatedTimestamp
     - DateTime
     - 
     - 
   * - AlarmDescription
     - String
     - 1 ~ 255  
     - Value consisting of only numbers can not be used.
   * - AlarmHistoryItems
     - AlarmHistoryItem list
     - 
     - 
   * - AlarmName
     - String
     - 1 ~ 255
     - Value consisting of only numbers can not be used.
   * - AlarmNamePrefix
     - String
     - 1 ~ 255
     - Value consisting of only numbers can not be used.
   * - AlarmNames
     - String list
     - 0 ~ 100
     - 
   * - Average
     - Double
     - 
     - 
   * - ComparisonOperator
     - String
     - 
     - GreaterThanOrEqualToThreshold | GreaterThanThreshold | 
       LessThanThreshold | LessThanOrEqualToThreshold
   * - Datapoints
     - Datapoint list
     - 
     - 
   * - Dimensions
     - Dimension list
     - 0 ~ 10
     - 
   * - EndDate
     - DateTime
     - 
     - 
   * - EndTime
     - DateTime
     - 
     - 
   * - EvaluationPeriods
     - Integer
     - 
     - 1 ~ 100
   * - HistoryItemType
     - String
     - 
     - ConfigurationUpdate | StateUpdate | Action
   * - HistorySummary
     - String
     - 1 ~ 255
     - 
   * - InsufficientDataActions
     - String
     - 
     - 
   * - Label
     - String
     - 
     - 
   * - Maximum
     - Double
     - 
     - 
   * - MaxRecords
     - Integer
     - 
     - 
   * - MetricAlarms
     - MetricAlarm list
     - 
     - 
   * - MetricData
     - MetricDatum list
     - 
     - 
   * - MetricName
     - String
     - 1 ~ 255
     - Value consisting of only numbers can not be used.
   * - Metrics
     - Metric list
     - 
     - 
   * - Minimum
     - Double
     - 
     - 
   * - Name
     - String
     - 1 ~ 255
     - 
   * - Namespace
     - String
     - 1 ~ 255
     - Value consisting of only numbers can not be used.
   * - NextToken
     - String
     - 
     - 
   * - OKActions
     - String
     - 
     - 
   * - Period
     - Integer
     - 
     - 60 ~ 86400, multiple of 60.
   * - SampleCount
     - Double
     - 
     - 
   * - StartDate
     - DateTime
     - 
     - 
   * - StartTime
     - DateTime
     - 
     - 
   * - StateReason
     - String
     - 1 ~ 1023
     - Value consisting of only numbers can not be used.
   * - StateReasonData
     - String
     - 0 ~ 4000
     - Value consisting of only numbers can not be used.
   * - StateValue
     - String
     - 
     - 
   * - Statistic 
     - String
     -
     - 
   * - Statistics 
     - String list
     - 1 ~ 5
     - 
   * - StatisticValues
     - TBD
     - 
     - Not yet implemented
   * - Sum
     - Double
     - 
     - 
   * - Threshold
     - Double
     - 
     - 
   * - Timestamp
     - DateTime
     - 
     - 
   * - Unit
     - String
     - 
     - Seconds | Microseconds | Milliseconds | Bytes | 
       Kilobytes | Megabytes | Gigabytes | Terabytes | Bits | Kilobits | 
       Megabits | Gigabits | Terabits | Percent | Count | Bytes/Second | 
       Kilobytes/Second | Megabytes/Second | Gigabytes/Second | 
       Terabytes/Second | Bits/Second | Kilobits/Second | Megabits/Second | 
       Gigabits/Second | Terabits/Second | Count/Second | None
   * - Value
     - String
     - 1 ~ 255
     - 
     