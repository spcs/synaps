# Copyright 2012 Samsung SDS
# All Rights Reserved

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

    def put_metric_data(self, context, namespace, metric_data, **kwargs):
        ret = self.monitor_api.put_metric_data(context, namespace, metric_data)
        return ret

    def get_metric_statistics(self, context, **kwargs):
        return {}

    def list_metrics(self, context, **kwargs):
        #<ListMetricsResponse xmlns="http://monitoring.amazonaws.com/doc/2010-08-01/">
        #  <ListMetricsResult>
        #    <Metrics>
        #      <member>
        #        <Dimensions>
        #          <member>
        #            <Name>InstanceId</Name>
        #            <Value>i-d8a598ba</Value>
        #          </member>
        #        </Dimensions>
        #        <MetricName>NetworkOut</MetricName>
        #        <Namespace>AWS/EC2</Namespace>
        #      </member>
        #    </Metrics>
        #  </ListMetricsResult>
        #  <ResponseMetadata>
        #    <RequestId>613102e7-6bff-11e1-9ea2-0fd041a23246</RequestId>
        #  </ResponseMetadata>
        #</ListMetricsResponse>

        return {
            "list_metrics_result": {
                "Metrics": [
                    {
                        'dimensions':{
                            'member':{
                                'name': 'InstanceId',
                                'value': 'i-d8a598ba'
                            }
                        },
                        'metric_name': 'NetworkOut',
                        'namespace': 'AWS/EC2'
                    }, {
                        'dimensions':{
                            'member':{
                                'name': 'InstanceId',
                                'value': 'i-d8a598ba'
                            }
                        },
                        'metric_name': 'NetworkOut',
                        'namespace': 'AWS/EC2'
                    },
                            
                ]
            }
        }


