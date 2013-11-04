# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
# Copyright 2012 Red Hat, Inc.
# Copyright (c) 2012 Samsung SDS Co., LTD
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

"""Command-line flag library.

Emulates gflags by wrapping cfg.ConfigOpts.

The idea is to move fully to cfg eventually, and this wrapper is a
stepping stone.

"""

import os
import socket
import sys

import gflags

from synaps.compat import flagfile
from synaps.openstack.common import cfg


class SynapsConfigOpts(cfg.CommonConfigOpts):

    def __init__(self, *args, **kwargs):
        super(SynapsConfigOpts, self).__init__(*args, **kwargs)
        self.disable_interspersed_args()

    def __call__(self, argv):
        with flagfile.handle_flagfiles_managed(argv[1:]) as args:
            return argv[:1] + super(SynapsConfigOpts, self).__call__(args)

def _wrapper(func):
    def _wrapped(*args, **kw):
        kw.setdefault('flag_values', FLAGS)
        func(*args, **kw)
    _wrapped.func_name = func.func_name
    return _wrapped

FLAGS = SynapsConfigOpts(project="synaps")

class UnrecognizedFlag(Exception):
    pass


def DECLARE(name, module_string, flag_values=FLAGS):
    if module_string not in sys.modules:
        __import__(module_string, globals(), locals())
    if name not in flag_values:
        raise UnrecognizedFlag('%s not defined by %s' % (name, module_string))


def _get_my_ip():
    """
    Returns the actual ip of the local machine.

    This code figures out what source address would be used if some traffic
    were to be sent out to some well known address on the Internet. In this
    case, a Google DNS server is used, but the specific address does not
    matter much.  No traffic is actually sent.
    """
    try:
        csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        csock.connect(('8.8.8.8', 80))
        (addr, port) = csock.getsockname()
        csock.close()
        return addr
    except socket.error:
        return "127.0.0.1"


log_opts = [
    cfg.StrOpt('logdir',
               default=None,
               help='output to a per-service log file in named directory'),
    cfg.StrOpt('logfile',
               default=None,
               help='output to named file'),
    cfg.BoolOpt('use_stderr',
                default=True,
                help='log to standard error'),
    cfg.BoolOpt('log_storm_worker',
                default=False,
                help='log to storm worker log'),
    cfg.BoolOpt('log_storm_file',
                default=True,
                help='log to file per storm executor process'),
    ]

core_opts = [
    cfg.StrOpt('cassandra_replication_factor',
               default='1',
               help='cassandra replication factor'),
    cfg.ListOpt('cassandra_server_list',
                default=['localhost:9160', ],
                help='cassandra cluster'),
    cfg.IntOpt('cassandra_timeout',
               default=10, # 5 seconds
               help='cassandra timeout'),             
    cfg.IntOpt('statistics_ttl',
               default=60 * 60 * 24 * 15, # 15 days in seconds
               help='time to live of statistics data'),
    cfg.IntOpt('left_offset',
               default=60 * 5, # 5 minutes in seconds
               help='start time of memory.'),
    cfg.IntOpt('right_offset',
               default=60 * 60, # 1 hour in seconds
               help='end time of memory.'),
    cfg.ListOpt('statistics_archives',
                default=['1', '5', '15', '60', '360', '1440'],
                help='intervals to store statistical metric data in minutes'),
    cfg.StrOpt('cassandra_keyspace',
               default='synaps_test',
               help='cassandra key space'),
    cfg.IntOpt('max_query_period_minutes',
               default=60 * 24 * 15, # 15 days in minutes
               help='max period to query at once'),
    cfg.IntOpt('max_query_datapoints',
               default=60 * 24, # 15 days in minutes
               help='max datapoints to query at once'),
    cfg.StrOpt('api_paste_config',
               default="api-paste.ini",
               help='File name for the paste.deploy config for synaps-api'),
    cfg.StrOpt('pybasedir',
               default=os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                    '../')),
               help='Directory where the nova python module is installed'),
    cfg.StrOpt('state_path',
               default=os.path.join(os.path.dirname(__file__), '../'),
               help="Top-level directory for maintaining synaps's state"),
    cfg.StrOpt('lock_path',
               default=os.path.join(os.path.dirname(__file__), '../'),
               help='Directory for lock files'),
    cfg.StrOpt('spcs_access_key_id',
               default='admin',
               help='SPCS Access ID'),
    cfg.StrOpt('spcs_secret_access_key',
               default='admin',
               help='SPCS Access Key'),
    cfg.StrOpt('smtp_server',
               default='mailin.samsung.com',
               help='Default mail server'),
    cfg.StrOpt('mail_sender',
               default='spcs@sdscloud.co.kr',
               help='Default mail sender'),
    cfg.BoolOpt('enable_send_mail',
                default=True,
                help='flag for mail send'),
    cfg.StrOpt('sms_sender',
               default='01012345678',
               help='Default SMS sender'),
    cfg.StrOpt('sms_database_host',
               default='localhost',
               help='Default SMS database'),
    cfg.IntOpt('sms_database_port',
               default=3306,
               help='Default SMS database port'),
    cfg.StrOpt('sms_database',
               default='synaps',
               help='Default SMS database'),
    cfg.StrOpt('sms_db_username',
               default='root',
               help='Default SMS database username'),
    cfg.StrOpt('sms_db_password',
               default='synaps',
               help='Default SMS database password'),
    cfg.BoolOpt('enable_send_sms',
                default=True,
                help='flag for sms send'),
    cfg.StrOpt('notification_bind_addr',
               default='tcp://*:31110',
               help='Synaps Notification Bind Address'),
    cfg.StrOpt('notification_server_addr',
               default='tcp://mail:31110',
               help='Synaps Notification Server'),
    cfg.StrOpt('cloudwatch_listen',
               default="0.0.0.0",
               help='IP address for cloudwatch API to listen'),
    cfg.IntOpt('cloudwatch_listen_port',
               default=8776,
               help='port for cloudwatch api to listen'),
    cfg.StrOpt('admin_namespace',
               default='SPCS/',
               help='admin namespace'),
    cfg.IntOpt('insufficient_buffer',
               default=3,
               help='time buffer to declare insufficient data(in minutes)')
    ]

debug_opts = []



global_opts = [
    cfg.StrOpt('my_ip',
               default=_get_my_ip(),
               help='host ip address'),
    cfg.StrOpt('cloudwatch_host',
               default='$my_ip',
               help='ip of api server'),
    cfg.StrOpt('cloudwatch_dmz_host',
               default='$my_ip',
               help='internal ip of api server'),
    cfg.IntOpt('cloudwatch_port',
               default=8776,
               help='cloud controller port'),
    cfg.StrOpt('cloudwatch_scheme',
               default='http',
               help='prefix for cloudwatch'),
    cfg.StrOpt('cloudwatch_path',
               default='/monitor',
               help='suffix for cloudwatch'),
    cfg.IntOpt('auth_token_ttl',
               default=3600,
               help='Seconds for auth tokens to linger'),
    cfg.StrOpt('logfile_mode',
               default='0644',
               help='Default file mode of the logs.'),
    cfg.ListOpt('memcached_servers',
                default=None,
                help='Memcached servers or None for in process cache.'),
    cfg.StrOpt('keystone_ec2_url',
               default='http://localhost:5000/v2.0/ec2tokens',
               help='Keystone EC2 token URL'),
]

rabbitmq_opts = [
    cfg.StrOpt('rabbit_host',
               default='mq01',
               help='the RabbitMQ host'),
    cfg.IntOpt('rabbit_port',
               default=5672,
               help='the RabbitMQ port'),
    cfg.StrOpt('rabbit_userid',
               default='guest',
               help='the RabbitMQ userid'),
    cfg.StrOpt('rabbit_password',
               default='guest',
               help='the RabbitMQ password'),
    cfg.StrOpt('rabbit_virtual_host',
               default='/',
               help='the RabbitMQ virtual host'),
    cfg.IntOpt('rabbit_read_workers',
               default=20,
               help='Number of workers for api spout'),
]

instance_action_opts = [
    cfg.BoolOpt('enable_instance_action',
                default=True,
                help='flag for instance action'),
    cfg.StrOpt('nova_auth_url',
                default='http://localhost:35357/v2.0',
                help='keystone host'),
    cfg.StrOpt('admin_tenant_name',
                default="service",
                help='admin tenant name'),                        
    cfg.StrOpt('admin_user',
                default="nova",
                help='admin user name'),                        
    cfg.StrOpt('admin_password',
                default="password",
                help='admin password name'),                        
]

stress_cli_opts = [
    cfg.IntOpt('stress_interval',
               default=55,
               help='Stress test interval'),
    cfg.IntOpt('stress_times',
               default=10,
               help='Number of stress test set'),
    cfg.IntOpt('stress_n_instances',
               default=100,
               help='Number of instances for stress test'),
    cfg.IntOpt('stress_metrics_per_instance',
               default=12,
               help='Number of metrics per instance for stress test'),
    cfg.BoolOpt('stress_backfill',
                default=False,
                help='backfill the metric data'),
]

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

FLAGS.register_cli_opts(log_opts)
FLAGS.register_cli_opts(core_opts)
FLAGS.register_cli_opts(debug_opts)
FLAGS.register_cli_opts(test_cli_opts)
FLAGS.register_cli_opts(stress_cli_opts)
FLAGS.register_opts(global_opts)
FLAGS.register_opts(rabbitmq_opts)
FLAGS.register_opts(instance_action_opts)
