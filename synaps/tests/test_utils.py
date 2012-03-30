# Copyright 2012 Samsung SDS
# All Rights Reserved

import unittest

from synaps import utils

class TestUtils(unittest.TestCase):

    def test_align_metrictime(self):
        actual = utils.align_metrictime(timestamp=90.0, resolution=60)
        self.assertEqual(actual, 120)

        actual = utils.align_metrictime(timestamp=100.0, resolution=60)
        self.assertEqual(actual, 120)

        actual = utils.align_metrictime(timestamp=120.0, resolution=60)
        self.assertEqual(actual, 120)

        actual = utils.align_metrictime(timestamp=125.0, resolution=60)
        self.assertEqual(actual, 120)

        actual = utils.align_metrictime(timestamp=149.0, resolution=60)
        self.assertEqual(actual, 120)

        actual = utils.align_metrictime(timestamp=150.0, resolution=60)
        self.assertEqual(actual, 180)

        actual = utils.align_metrictime(timestamp=170.1, resolution=60)
        self.assertEqual(actual, 180)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
