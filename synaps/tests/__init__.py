# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright (c) 2012 Samsung SDS Co., LTD
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import atexit
from datetime import datetime
import testresources
import testtools
import uuid
import fixtures
import functools
import nose.plugins.attrib
from boto.ec2 import regioninfo
from boto.ec2.cloudwatch import CloudWatchConnection
import sys
import os
from synaps import flags

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir, os.pardir))
if os.path.exists(os.path.join(possible_topdir, "synaps", "__init__.py")):
    sys.path.insert(0, possible_topdir)

flags.FLAGS(sys.argv)
FLAGS = flags.FLAGS

at_exit_set = set()

def validate_tearDownClass():
    if at_exit_set:
        raise RuntimeError("tearDownClass does not calls the super's "
                           "tearDownClass in these classes: "
                           + str(at_exit_set))

atexit.register(validate_tearDownClass)


def get_cloudwatch_client(access_key=None, secret_key=None):
    region = regioninfo.RegionInfo(None, 'Test', FLAGS.get('test_synaps_ip'))
    ak = access_key or FLAGS.get('test_access_key')  
    sk = secret_key or FLAGS.get('test_secret_key')
    return CloudWatchConnection(
                aws_access_key_id=ak, aws_secret_access_key=sk,
                is_secure=False, port=FLAGS.get('test_synaps_port'),
                path=FLAGS.get('test_synaps_path'), region=region)


class BaseTestCase(testtools.TestCase,
                     testtools.testcase.WithAttributes,
                     testresources.ResourcedTestCase):
    
    setUpClassCalled = False

    @classmethod
    def setUpClass(cls):
        if hasattr(super(BaseTestCase, cls), 'setUpClass'):
            super(BaseTestCase, cls).setUpClass()
        cls.setUpClassCalled = True

    @classmethod
    def tearDownClass(cls):
        at_exit_set.discard(cls)
        if hasattr(super(BaseTestCase, cls), 'tearDownClass'):
            super(BaseTestCase, cls).tearDownClass()
                
    def setUp(self):
        super(BaseTestCase, self).setUp()
        if not self.setUpClassCalled:
            raise RuntimeError("setUpClass does not calls the super's"
                               "setUpClass in the "
                               + self.__class__.__name__)
        at_exit_set.add(self.__class__)
        test_timeout = os.environ.get('OS_TEST_TIMEOUT', 0)
        try:
            test_timeout = int(test_timeout)
        except ValueError:
            test_timeout = 0
        if test_timeout > 0:
            self.useFixture(fixtures.Timeout(test_timeout, gentle=True))

        if (os.environ.get('OS_STDOUT_CAPTURE') == 'True' or
                os.environ.get('OS_STDOUT_CAPTURE') == '1'):
            stdout = self.useFixture(fixtures.StringStream('stdout')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stdout', stdout))
        if (os.environ.get('OS_STDERR_CAPTURE') == 'True' or
                os.environ.get('OS_STDERR_CAPTURE') == '1'):
            stderr = self.useFixture(fixtures.StringStream('stderr')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stderr', stderr))
        if (os.environ.get('OS_LOG_CAPTURE') != 'False' and
            os.environ.get('OS_LOG_CAPTURE') != '0'):
            log_format = '%(asctime)-15s %(message)s'
            self.useFixture(fixtures.LoggerFixture(nuke_handlers=False,
                                                   format=log_format,
                                                   level=None))        


class SynapsTestCase(BaseTestCase):
    def setUp(self):    
        super(SynapsTestCase, self).setUp()
        
        self.synaps = get_cloudwatch_client()
        self.synaps_bad_ak = get_cloudwatch_client(access_key="bad_ak")
        self.synaps_bad_sk = get_cloudwatch_client(secret_key="bad_sk")
        self.namespace = "TEST/" + datetime.now().strftime("%Y%m%d%H%M")
        self.metric_name = "test_metric"
        self.dimensions = {'instance_name':'test instance'}
        
    def generate_random_name(self, prefix=""):
        return prefix + str(uuid.uuid4())
    

def attr(*args, **kwargs):
    """A decorator which applies the nose and testtools attr decorator

    This decorator applies the nose attr decorator as well as the
    the testtools.testcase.attr if it is in the list of attributes
    to testtools we want to apply.
    """

    def decorator(f):
        if 'type' in kwargs and isinstance(kwargs['type'], str):
            f = testtools.testcase.attr(kwargs['type'])(f)
            if kwargs['type'] == 'smoke':
                f = testtools.testcase.attr('gate')(f)
        elif 'type' in kwargs and isinstance(kwargs['type'], list):
            for attr in kwargs['type']:
                f = testtools.testcase.attr(attr)(f)
                if attr == 'smoke':
                    f = testtools.testcase.attr('gate')(f)
        return nose.plugins.attrib.attr(*args, **kwargs)(f)

    return decorator


def stresstest(*args, **kwargs):
    """Add stress test decorator

    For all functions with this decorator a attr stress will be
    set automatically.

    @param class_setup_per: allowed values are application, process, action
           ``application``: once in the stress job lifetime
           ``process``: once in the worker process lifetime
           ``action``: on each action
    @param allow_inheritance: allows inheritance of this attribute
    """
    def decorator(f):
        if 'class_setup_per' in kwargs:
            setattr(f, "st_class_setup_per", kwargs['class_setup_per'])
        else:
            setattr(f, "st_class_setup_per", 'process')
        if 'allow_inheritance' in kwargs:
            setattr(f, "st_allow_inheritance", kwargs['allow_inheritance'])
        else:
            setattr(f, "st_allow_inheritance", False)
        attr(type='stress')(f)
        return f
    return decorator


def skip_because(*args, **kwargs):
    """A decorator useful to skip tests hitting known bugs

    @param bug: bug number causing the test to skip
    @param condition: optional condition to be True for the skip to have place
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*func_args, **func_kwargs):
            if "bug" in kwargs:
                if "condition" not in kwargs or kwargs["condition"] is True:
                    msg = "Skipped until Bug: %s is resolved." % kwargs["bug"]
                    raise testtools.TestCase.skipException(msg)
            return f(*func_args, **func_kwargs)
        return wrapper
    return decorator
