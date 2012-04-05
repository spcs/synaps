# Copyright 2012 Samsung SDS
# All Rights Reserved

from synaps.monitor.api import API

class Datapoint(object):
    """
    The Datapoint data type encapsulates the statistical data that Amazon 
    CloudWatch computes from metric data.
    
    Average    
        The average of metric values that correspond to the datapoint.
        Type: Double

    Maximum    
        The maximum of the metric value used for the datapoint.
        Type: Double

    Minimum    
        The minimum metric value used for the datapoint.
        Type: Double
    
    SampleCount    
        The number of metric values that contributed to the aggregate value of 
        this datapoint.
        Type: Double

    Sum    
        The sum of metric values used for the datapoint.
        Type: Double

    Timestamp    
        The time stamp used for the datapoint.
        Type: DateTime

    Unit    
        The standard unit used for the datapoint.
        Type: String
        
        Valid Values: Seconds | Microseconds | Milliseconds | Bytes | 
                      Kilobytes | Megabytes | Gigabytes | Terabytes | Bits | 
                      Kilobits | Megabits | Gigabits | Terabits | Percent | 
                      Count | Bytes/Second | Kilobytes/Second | 
                      Megabytes/Second | Gigabytes/Second | Terabytes/Second | 
                      Bits/Second | Kilobits/Second | Megabits/Second | 
                      Gigabits/Second | Terabits/Second | Count/Second | None
    """
    
class Dimension(object):
    """
    The Dimension data type further expands on the identity of a metric using 
    a Name, Value pair.

    For examples that use one or more dimensions, see PutMetricData.

    Name    
        The name of the dimension.
        Type: String
        Length constraints: Minimum length of 1. Maximum length of 255.

    Value    
        The value representing the dimension measurement
        Type: String
        Length constraints: Minimum length of 1. Maximum length of 255.
    """    
    
class DimensionFilter(object):
    """
    The DimensionFilter data type is used to filter ListMetrics results.

    Name    
        The dimension name to be matched.
        Type: String
        Length constraints: Minimum length of 1. Maximum length of 255.

    Value    
        The value of the dimension to be matched.
        Note: Specifying a Name without specifying a Value returns all values 
        associated with that Name.
        Type: String
        Length constraints: Minimum length of 1. Maximum length of 255.
    """

class GetMetricStatisticsResult(object):
    """
    The output for the GetMetricStatistics action.
    
    Datapoints    
        The datapoints for the specified metric.
        Type: Datapoint list

    Label    
        A label describing the specified metric.
        Type: String
    """

class ListMetricsResult(object):
    """
    The output for the ListMetrics action.

    Metrics    
        A list of metrics used to generate statistics for an AWS account.
        Type: Metric list

    NextToken    
        A string that marks the start of the next batch of returned results.
        Type: String
    """
    
class Metric(object):
    """
    The Metric data type contains information about a specific metric. If you 
    call ListMetrics, Amazon CloudWatch returns information contained by this 
    data type.

    The example in the Examples section publishes two metrics named buffers 
    and latency. Both metrics are in the examples namespace. Both metrics have 
    two dimensions, InstanceID and InstanceType.

    Dimensions    
        A list of dimensions associated with the metric.
        Type: Dimension list
        Length constraints: Minimum of 0 item(s) in the list. Maximum of 10 
        item(s) in the list.

    MetricName    
        The name of the metric.
        Type: String
        Length constraints: Minimum length of 1. Maximum length of 255.

    Namespace    
        The namespace of the metric.
        Type: String
        Length constraints: Minimum length of 1. Maximum length of 255.
    """

class MetricDatum(object):
    """
    The MetricDatum data type encapsulates the information sent with 
    PutMetricData to either create a new metric or add new values to be 
    aggregated into an existing metric.
    
    Dimensions    
        A list of dimensions associated with the metric.
        Type: Dimension list
        Length constraints: Minimum of 0 item(s) in the list. Maximum of 10 
        item(s) in the list.

    MetricName    
        The name of the metric.
        Type: String
        Length constraints: Minimum length of 1. Maximum length of 255.

    StatisticValues    
        A set of statistical values describing the metric.
        Type: StatisticSet

    Timestamp    
        The time stamp used for the metric. If not specified, the default 
        value is set to the time the metric data was received.
        Type: DateTime

    Unit    
        The unit of the metric.
        Type: String
        Valid Values: Seconds | Microseconds | Milliseconds | Bytes | 
                      Kilobytes | Megabytes | Gigabytes | Terabytes | Bits | 
                      Kilobits | Megabits | Gigabits | Terabits | Percent | 
                      Count | Bytes/Second | Kilobytes/Second | 
                      Megabytes/Second | Gigabytes/Second | Terabytes/Second | 
                      Bits/Second | Kilobits/Second | Megabits/Second | 
                      Gigabits/Second | Terabits/Second | Count/Second | None

    Value    
        The value for the metric.

        Important: Although the Value parameter accepts numbers of type 
        Double, Amazon CloudWatch truncates values with very large exponents. 
        Values with base-10 exponents greater than 126 (1 x 10^126) are 
        truncated. Likewise, values with base-10 exponents less than -130 
        (1 x 10^-130) are also truncated.

        Type: Double
    """
    
class StatisticSet(object):
    """
    The StatisticSet data type describes the StatisticValues component of 
    MetricDatum, and represents a set of statistics that describes a specific 
    metric.

    Maximum    
        The maximum value of the sample set.
        Type: Double

    Minimum    
        The minimum value of the sample set.
        Type: Double
    
    SampleCount    
        The number of samples used for the statistic set.
        Type: Double

    Sum    
        The sum of values for the sample set.
        Type: Double
    """
