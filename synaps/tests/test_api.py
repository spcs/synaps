# Copyright 2012 Samsung SDS
# All Rights Reserved

import uuid
import unittest
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
        N_DATA = 100
        metric_name = uuid.uuid4().get_hex()
        n_metrics_before = len(self.synaps.list_metrics())
        
        for i in range(N_DATA):
            # 1.1. first dimension is {'test id':'synaps test'}
            synaps_ret = self.synaps.put_metric_data(
                namespace="SPCS/SYNAPSTEST",
                name=metric_name,
                value=i * 1.0,
                unit="Percent",
                dimensions={'test id':'synaps test'},
            )
            self.assertTrue(synaps_ret)

            # 1.2. 2nd dimension is {'test id':'synaps test2'}
            synaps_ret = self.synaps.put_metric_data(
                namespace="SPCS/SYNAPSTEST",
                name=metric_name,
                value=i * 1.0,
                unit="Percent",
                dimensions={'test id':'synaps test2'},
            )
            self.assertTrue(synaps_ret)            

        # 2. check if the metrics are created properly
        # 2.1. fetch metrics using 1st dimensions 
        synaps_metrics = self.synaps.list_metrics(
            dimensions={'test id':'synaps test'},
            metric_name=metric_name,
            namespace='SPCS/SYNAPSTEST'
        )
        
        self.assertEqual(len(synaps_metrics), 1)
        metric = synaps_metrics[0]
        self.assertEqual(metric.name, metric_name)
        self.assertEqual(metric.namespace, 'SPCS/SYNAPSTEST')
        # TODO(june.yi): need to check dimension
        
        # 2.2. fetch metrics without dimensions. The result of this call 
        # should returns two metrics.
        synaps_metrics = self.synaps.list_metrics(
            metric_name=metric_name,
            namespace='SPCS/SYNAPSTEST'
        )
        self.assertEqual(len(synaps_metrics), 2)

        # 2.3. number of metrics are increased by 2 due to this test
        n_metrics_after = len(self.synaps.list_metrics())
        self.assertEqual(n_metrics_before + 2, n_metrics_after)
    
if __name__ == "__main__":
    unittest.main()
