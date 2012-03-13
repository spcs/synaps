import unittest
import datetime
from boto.ec2 import regioninfo
from boto.ec2.cloudwatch import CloudWatchConnection

class ApiCloudwatchTestCase(unittest.TestCase):
    def setUp(self):
        self.cloudwatch = CloudWatchConnection(
            aws_access_key_id="AKIAIUIUQBYNQ3G327RA",
            aws_secret_access_key="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"
        )

        self.synaps = CloudWatchConnection(
            aws_access_key_id='AKIAIUIUQBYNQ3G327RA',
            aws_secret_access_key='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',
            is_secure=False,
            port=8773,
            region=regioninfo.RegionInfo(None, 'test', '127.0.0.1'),
            path='/monitor'
        )
    
    def tearDown(self):
        pass
        
    def test_put_metric_data(self):
#        self.cloudwatch.put_metric_data()
        pass
        
    def test_get_metric_statistics(self):
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(hours=1 * 24)
        period = 5 * 60 # 5min
        metric_name = u'Network'
        namespace = u'AWS/EC2'
        statistics = ['SampleCount', 'Average']
        dimensions = {u'InstanceId': [u'i-0031ee62']}
        
        cloudwatch_stat = self.cloudwatch.get_metric_statistics(
            period=period,
            start_time=start_time,
            end_time=end_time,
            metric_name=metric_name,
            namespace=namespace,
            statistics=statistics,
            dimensions=dimensions
        )
        
        synaps_stat = self.synaps.get_metric_statistics(
            period=period,
            start_time=start_time,
            end_time=end_time,
            metric_name=metric_name,
            namespace=namespace,
            statistics=statistics,
            dimensions=dimensions
        )
    
    def test_list_metrics(self):
        cloudwatch_metrics = self.cloudwatch.list_metrics()
        synaps_metrics = self.synaps.list_metrics()
        print cloudwatch_metrics
        print synaps_metrics
#        self.assertEqual(cloudwatch_metrics, synaps_metrics)

if __name__ == "__main__":
    unittest.main()
