# Copyright 2012 Samsung SDS
# All Rights Reserved

import datetime

from synaps import log as logging
from synaps import monitor
from synaps import exception

LOG = logging.getLogger(__name__)


class MonitorController(object):
    """ MonitorController provides the critical dispatch between
 inbound API calls through the endpoint and messages
 sent to the other nodes.
"""
    def __init__(self):
        self.monitor_api = monitor.API()

    def __str__(self):
        return 'MonitorController'

    def put_metric_data(self, context, namespace, metric_data):
        """
        Publishes metric data points to Synaps. If specified metric does not
        exist, Synaps creates the metric.
        """
        self.monitor_api.put_metric_data(context, namespace, metric_data)
        return {}

    def get_metric_statistics(self, context, end_time, metric_name,
                              namespace, period, start_time, statistics,
                              unit="None", dimensions=None):
        """
        Gets statistics for the specified metric.        

<GetMetricStatisticsResponse xmlns="http://monitoring.amazonaws.com/doc/2010-08-01/">
  <GetMetricStatisticsResult>
    <Datapoints>
      <member>
        <Timestamp>2012-03-29T16:54:00Z</Timestamp>
        <Unit>Percent</Unit>
        <Sum>249.13999999999982</Sum>
        <Average>0.2783687150837987</Average>
      </member>
      <member>
        <Timestamp>2012-03-26T16:54:00Z</Timestamp>
        <Unit>Percent</Unit>
        <Sum>412.63999999999965</Sum>
        <Average>0.2865555555555553</Average>
      </member>
      <member>
        <Timestamp>2012-03-25T16:54:00Z</Timestamp>
        <Unit>Percent</Unit>
        <Sum>584.3400000000007</Sum>
        <Average>0.4063560500695415</Average>
      </member>
      <member>
        <Timestamp>2012-03-27T16:54:00Z</Timestamp>
        <Unit>Percent</Unit>
        <Sum>395.97999999999934</Sum>
        <Average>0.27498611111111065</Average>
      </member>
      <member>
        <Timestamp>2012-03-23T16:54:00Z</Timestamp>
        <Unit>Percent</Unit>
        <Sum>378.1199999999996</Sum>
        <Average>0.2640502793296087</Average>
      </member>
      <member>
        <Timestamp>2012-03-24T16:54:00Z</Timestamp>
        <Unit>Percent</Unit>
        <Sum>654.5700000000021</Sum>
        <Average>0.4590252454417967</Average>
      </member>
      <member>
        <Timestamp>2012-03-28T16:54:00Z</Timestamp>
        <Unit>Percent</Unit>
        <Sum>389.37999999999926</Sum>
        <Average>0.27040277777777727</Average>
      </member>
    </Datapoints>
    <Label>CPUUtilization</Label>
  </GetMetricStatisticsResult>
  <ResponseMetadata>
    <RequestId>84e4db0e-7a3d-11e1-9991-1b2df6a17f8d</RequestId>
  </ResponseMetadata>
</GetMetricStatisticsResponse>"""        
        
        
        datapoints = [{'Timestamp':datetime.datetime.now(),
                       'Unit':'Percent',
                       'Sum':12.32,
                       'Average':-2.32}]
        label = "hohoho"
        
        return {'GetMetricStatisticsResult': {'Datapoints': datapoints,
                                              'Label': label}}

    def list_metrics(self, context, next_token=None, dimensions=None,
                     metric_name=None, namespace=None):
        """
        Returns a list of valid metrics stored for the Synaps account owner. 
        Returned metrics can be used with get_metric_statics to obtain 
        statistical data for a given metric.
        """

        def to_aws_metric(metric):
            def to_aws_dimensions(dimensions):
                return [{'name':k, 'value':v} for k, v in dimensions.items()]
            
            k, v = metric
            ret = {}
            ret['dimensions'] = to_aws_dimensions(v['dimensions'])
            ret['metric_name'] = v['name']
            ret['namespace'] = v['namespace']
            return ret
        
        metrics = self.monitor_api.list_metrics(context, next_token, dimensions,
                                                metric_name, namespace)
        metrics = map(to_aws_metric, metrics)
        
        return {'ListMetricsResult': {'Metrics': metrics}}
