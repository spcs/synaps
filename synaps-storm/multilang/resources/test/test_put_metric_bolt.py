'''
Created on Jun 5, 2012

@author: june
'''
import unittest
import uuid
from put_metric_bolt import PutMetricBolt
from storm import Tuple 

def make_tuple(values):
    return Tuple(None, None, None, None, values)

class Test(unittest.TestCase):
    def setUp(self):
        self.bolt = PutMetricBolt()

    def testProcess(self):
        values = [str(uuid.uuid4()), "{}"]
        self.bolt.initialize(None, None)
        self.bolt.process(make_tuple(values))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
