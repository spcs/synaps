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

from storm import Spout, emit, log
from time import sleep
from uuid import uuid4
import json
from synaps_constants import PUT_METRIC_DATA_MSG_ID

class ApiSpout(Spout):
    def nextTuple(self):
        sleep(0.5)
        id = str(uuid4())
        message = {'msg_id':PUT_METRIC_DATA_MSG_ID, 'contents': "test message"}
        message_json = json.dumps(message)
        emit([message_json], id=id)

if __name__ == "__main__":
    flags.FLAGS(sys.argv)
    utils.default_flagfile()
    ApiSpout().run()
