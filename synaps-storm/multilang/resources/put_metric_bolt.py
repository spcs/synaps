#!/usr/bin/env python
# Copyright 2012 Samsung SDS

import pycassa
import os
import sys

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "synaps", "__init__.py")):
    sys.path.insert(0, possible_topdir)

from synaps import flags
from synaps import log as logging
from synaps import utils

import storm
import json
from synaps_constants import PUT_METRIC_DATA_MSG_ID

class PutMetricBolt(storm.BasicBolt):
    def process(self, tup):
        storm.log(str(tup.values))

PutMetricBolt().run()
