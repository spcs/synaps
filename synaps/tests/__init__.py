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

from boto.ec2 import regioninfo
from boto.ec2.cloudwatch import CloudWatchConnection

from synaps.openstack.common import cfg
from synaps import flags

test_cli_opts = [
    cfg.StrOpt('test_access_key',
                default='changeme',
                help='Synaps API access key for test'),
    cfg.StrOpt('test_secret_key',
               default='changeme',
               help='Synaps API secret key for test'),
    cfg.StrOpt('test_synaps_ip',
               default='127.0.0.1',
               help='Synaps API IP address for test'),
    cfg.StrOpt('test_synaps_path',
               default='/monitor',
               help='Synaps API service path for test'),
    cfg.IntOpt('test_synaps_port',
               default=3776,
               help='Synaps API service port for test'),
]

FLAGS = flags.FLAGS
FLAGS.register_opts(test_cli_opts)

def get_cloudwatch_client():
    region = regioninfo.RegionInfo(None, 'Test', FLAGS.get('test_synaps_ip'))
    return CloudWatchConnection(
                aws_access_key_id=FLAGS.get('test_access_key'),
                aws_secret_access_key=FLAGS.get('test_secret_key'),
                is_secure=False,
                port=FLAGS.get('test_synaps_port'),
                path=FLAGS.get('test_synaps_path'),
                region=region)    

