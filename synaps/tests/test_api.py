# Copyright 2012 Samsung SDS
# All Rights Reserved

import datetime
import uuid
import unittest
from collections import OrderedDict
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

    def test_metric_scenario1(self):
        """
        This test case covers followings APIs.
         
        * put_metric_data
        * list_metrics
        
        """    
        # 1. create new metric and put N data into two different dimensions
        now = datetime.datetime.now()
        minute = datetime.timedelta(seconds=60)
        start_time = now
        end_time = start_time - 60 * minute
        
        N_DATA = 60
        metric_name = uuid.uuid4().get_hex()
        n_metrics_before = len(self.synaps.list_metrics())
        namespace = "SPCS/SYNAPSTEST"
        dimensions1 = OrderedDict((("dimensions", "test1"),))
        dimensions2 = OrderedDict((("dimensions", "test2"),))        
        for i in range(N_DATA):
            # 1.1. first dimension is {'test id':'synaps test'}
            synaps_ret = self.synaps.put_metric_data(
                namespace=namespace,
                name=metric_name,
                value=i * 1.0,
                unit="Percent",
                dimensions=dimensions1,
                timestamp=start_time - i * minute,
            )
            self.assertTrue(synaps_ret)

            # 1.2. 2nd dimension is {'test id':'synaps test2'}
            synaps_ret = self.synaps.put_metric_data(
                namespace=namespace,
                name=metric_name,
                value=i * 1.0,
                unit="Percent",
                dimensions=dimensions2,
                timestamp=start_time - i * minute,
            )
            self.assertTrue(synaps_ret)            

        # 2. check if the metrics are created properly
        # 2.1. fetch metrics using 1st dimensions 
        synaps_metrics = self.synaps.list_metrics(
            dimensions=dimensions1,
            metric_name=metric_name,
            namespace=namespace
        )
        
        self.assertEqual(len(synaps_metrics), 1)
        metric = synaps_metrics[0]
        self.assertEqual(metric.name, metric_name)
        self.assertEqual(metric.namespace, namespace)
        
        # 2.2. fetch metrics without dimensions. The result of this call 
        # should returns two metrics.
        synaps_metrics = self.synaps.list_metrics(
            metric_name=metric_name,
            namespace=namespace
        )
        self.assertEqual(len(synaps_metrics), 2)

        # 2.3. number of metrics are increased by 2 due to this test
        n_metrics_after = len(self.synaps.list_metrics())
        self.assertEqual(n_metrics_before + 2, n_metrics_after)
        
        ##
        metric_name = metric_name
        namespace = namespace
        statistics = ["Average", "Sum"]
        dimensions = dimensions1
        unit = "Percent"
        
        stats = self.synaps.get_metric_statistics(300, start_time, end_time,
                                                  metric_name, namespace,
                                                  statistics, dimensions, unit)
        self.assertEqual(len(stats), 20)

#    def test_metric_scenario2(self):
#        """
#        hmm..
#        """
#        end_time = datetime.datetime.now()
#        start_time = end_time - datetime.timedelta(hours=24 * 7)
#        metric_name = u"CPUUtilization"
#        namespace = u"AWS/EC2"
#        statistics = [u"Average", "Sum"]
#        dimensions = OrderedDict((("InstanceId", "i-0031ee62"),)) 
#        #[{u'InstanceId': u'i-0031ee62'}]
#        unit = "None"
#        
#        for m in self.cloudwatch.list_metrics(dimensions=dimensions):
#            print m.name
#            print m.dimensions
#        
#        ret = self.cloudwatch.get_metric_statistics(period=3600*24,
#                  start_time=start_time, end_time=end_time,
#                  metric_name=metric_name, namespace=namespace,
#                  statistics=statistics, dimensions=dimensions, unit="Percent")
#        print ret
        
if __name__ == "__main__":
    unittest.main()
