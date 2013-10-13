# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2011 Justin Santa Barbara
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

import contextlib
import os
import sys
import tempfile
import uuid
import datetime
import shlex
import pyclbr
import random
import inspect
import socket
import re
import types
import time
import calendar
import netaddr
import shutil
import json
import itertools
from collections import OrderedDict
from xml.sax import saxutils

from eventlet import greenthread
from eventlet.green import subprocess

from synaps import flags
from synaps import exception
from synaps import log as logging
from synaps.openstack.common import cfg

from novaclient.v1_1 import client

LOG = logging.getLogger(__name__)
ISO_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
PERFECT_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
PERFECT_TIME_FORMAT_Z = "%Y-%m-%dT%H:%M:%S.%fZ"
NO_MS_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
FLAGS = flags.FLAGS

FLAGS.register_opt(
    cfg.BoolOpt('disable_process_locking', default=False,
                help='Whether to disable inter-process locks'))

RE_INTERNATIONAL_PHONENUMBER = re.compile("^\+[0-9]{7,17}$")
RE_EMAIL = re.compile('^[_.0-9a-z-]+@([0-9a-z][0-9a-z-]+.)+[a-z]{2,4}$')
RE_UUID = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
RE_INSTANCE_ACTION = re.compile('^InstanceAction:(Reboot|Migrate)\((%s)\)' % 
                                RE_UUID)

UNIT_CONV_MAP = {
    'None': 1.0,
    'Seconds': 1.0,
    'Bytes':1.0,
    'Bytes/Second':1.0, # std: Bytes/Second
    'Percent': 1.0,
    'Count': 1.0,
    'Count/Second': 1.0,
    'Microseconds': 10.0 ** (-6), # std: Seconds
    'Milliseconds': 10.0 ** (-3), # std: Seconds
    'Kilobytes':2.0 ** 10, # std: Bytes
    'Megabytes':2.0 ** 20, # std: Bytes
    'Gigabytes':2.0 ** 30, # std: Bytes
    'Terabytes':2.0 ** 40, # std: Bytes
    'Bits':2.0 ** (-3), # std: Bytes
    'Kilobits':2.0 ** 7, # std: Bytes
    'Megabits':2.0 ** 17, # std: Bytes
    'Gigabits':2.0 ** 27, # std: Bytes
    'Terabits':2.0 ** 37, # std: Bytes
    'Kilobytes/Second':10.0 ** 3, # std: Bytes/Second
    'Megabytes/Second':10.0 ** 6, # std: Bytes/Second
    'Gigabytes/Second':10.0 ** 9, # std: Bytes/Second
    'Terabytes/Second':10.0 ** 12, # std: Bytes/Second
    'Bits/Second':2.0 ** (-3), # std: Bytes/Second
    'Kilobits/Second':2.0 ** 7, # std: Bytes/Second
    'Megabits/Second':2.0 ** 17, # std: Bytes/Second
    'Gigabits/Second':2.0 ** 27, # std: Bytes/Second
    'Terabits/Second':2.0 ** 37, # std: Bytes/Second
}

UNITS = UNIT_CONV_MAP.keys()

def validate_email(email):
    try:
        ret = RE_EMAIL.match(email) is not None
    except TypeError:
        ret = False
    return ret


def validate_instance_action(instance_action):
    try:
        ret = RE_INSTANCE_ACTION.match(instance_action) is not None
    except TypeError:
        ret = False
    return ret


def parse_instance_action(instance_action):
    mobj = RE_INSTANCE_ACTION.match(instance_action)
    return mobj.groups() if mobj else None 


def validate_international_phonenumber(number):
    """
    International Telecommunication Union ITU-T Rec. E.123 (02/2001) 
    
    Notation for national and international telephone numbers, e-mail addresses 
    and web addresses
    """
    try:
        head, tail = number.split(' ', 1)
    except ValueError:
        return False
    
    number = head + tail.replace(' ', '')
    return RE_INTERNATIONAL_PHONENUMBER.match(number) is not None

def to_unit(value, unit):
    if not unit:
        unit = "None"
    return value / UNIT_CONV_MAP[unit]

def to_default_unit(value, unit):
    if not unit:
        unit = "None"
    return value * UNIT_CONV_MAP[unit]

def to_primitive(value, convert_instances=False, level=0):
    """Convert a complex object into primitives.

    Handy for JSON serialization. We can optionally handle instances,
    but since this is a recursive function, we could have cyclical
    data structures.

    To handle cyclical data structures we could track the actual objects
    visited in a set, but not all objects are hashable. Instead we just
    track the depth of the object inspections and don't go too deep.

    Therefore, convert_instances=True is lossy ... be aware.

    """
    nasty = [inspect.ismodule, inspect.isclass, inspect.ismethod,
             inspect.isfunction, inspect.isgeneratorfunction,
             inspect.isgenerator, inspect.istraceback, inspect.isframe,
             inspect.iscode, inspect.isbuiltin, inspect.isroutine,
             inspect.isabstract]
    for test in nasty:
        if test(value):
            return unicode(value)

    # value of itertools.count doesn't get caught by inspects
    # above and results in infinite loop when list(value) is called.
    if type(value) == itertools.count:
        return unicode(value)

    # FIXME(vish): Workaround for LP bug 852095. Without this workaround,
    #              tests that raise an exception in a mocked method that
    #              has a @wrap_exception with a notifier will fail. If
    #              we up the dependency to 0.5.4 (when it is released) we
    #              can remove this workaround.
    if getattr(value, '__module__', None) == 'mox':
        return 'mock'

    if level > 3:
        return '?'

    # The try block may not be necessary after the class check above,
    # but just in case ...
    try:
        if isinstance(value, (list, tuple)):
            o = []
            for v in value:
                o.append(to_primitive(v, convert_instances=convert_instances,
                                      level=level))
            return o
        elif isinstance(value, dict):
            o = {}
            for k, v in value.iteritems():
                o[k] = to_primitive(v, convert_instances=convert_instances,
                                    level=level)
            return o
        elif isinstance(value, datetime.datetime):
            return str(value)
        elif hasattr(value, 'iteritems'):
            return to_primitive(dict(value.iteritems()),
                                convert_instances=convert_instances,
                                level=level)
        elif hasattr(value, '__iter__'):
            return to_primitive(list(value), level)
        elif convert_instances and hasattr(value, '__dict__'):
            # Likely an instance of something. Watch for cycles.
            # Ignore class member vars.
            return to_primitive(value.__dict__,
                                convert_instances=convert_instances,
                                level=level + 1)
        else:
            return value
    except TypeError, e:
        # Class objects are tricky since they may define something like
        # __iter__ defined but it isn't callable as list().
        return unicode(value)

def dumps(value):
    try:
        return json.dumps(value)
    except TypeError:
        pass
    return json.dumps(to_primitive(value))

def gen_uuid():
    return uuid.uuid4()

def utcnow():
    """Overridable version of utils.utcnow."""
    if utcnow.override_time:
        return utcnow.override_time
    return datetime.datetime.utcnow()

utcnow.override_time = None

def align_metrictime(timestamp, resolution=60):
    """
    Align timestamp of metric for statistics 
    
      >>> align_metrictime(35.0, 60.0)
      60.0
      >>> align_metrictime(60.0, 60.0)
      120.0
      >>> align_metrictime(150.0, 60.0)
      180.0
      >>> align_metrictime(150.1, 60.0)
      180.0       
    """
    mod = int(datetime_to_timestamp(timestamp)) / resolution
    return datetime.datetime.utcfromtimestamp((mod + 1) * resolution)

def str_to_timestamp(timestr, fmt=PERFECT_TIME_FORMAT):
    if isinstance(timestr, str):
        at = parse_strtime(timestr, fmt)
        return time.mktime(at.timetuple())
    else:
        return time.time()

def parse_strtime(timestr, fmt=PERFECT_TIME_FORMAT):
    """Turn a formatted time back into a datetime."""
    if timestr.endswith('Z'):
        timestr = timestr[:-1]

    try:
        ret = datetime.datetime.strptime(timestr, fmt)
    except ValueError:
        ret = datetime.datetime.strptime(timestr, NO_MS_TIME_FORMAT)
        
    return ret

def strtime(at=None, fmt=PERFECT_TIME_FORMAT):
    """Returns formatted utcnow."""
    if not at:
        at = utcnow()
    return at.strftime(fmt)

def strtime_trunk(at=None):
    """Returns formatted utcnow."""
    strt = strtime(at,PERFECT_TIME_FORMAT_Z)
    return strt[:-5]+"Z"

def to_ascii(utf8):
    if isinstance(utf8, unicode):
        return utf8.encode('ascii')
    assert isinstance(utf8, str)
    return utf8

def utf8(value):
    """Try to turn a string into utf-8 if possible.

    Code is directly from the utf8 function in
    http://github.com/facebook/tornado/blob/master/tornado/escape.py

    """
    if isinstance(value, unicode):
        return value.encode('utf-8')
    assert isinstance(value, str)
    return value

def import_class(import_str):
    """Returns a class from a string including module and class."""
    mod_str, _sep, class_str = import_str.rpartition('.')
    try:
        __import__(mod_str)
        return getattr(sys.modules[mod_str], class_str)
    except (ImportError, ValueError, AttributeError), exc:
        LOG.debug(_('Inner Exception: %s'), exc)
        raise exception.ClassNotFound(class_name=class_str, exception=exc)

def monkey_patch():
    """  If the Flags.monkey_patch set as True,
    this function patches a decorator
    for all functions in specified modules.
    You can set decorators for each modules
    using FLAGS.monkey_patch_modules.
    The format is "Module path:Decorator function".
    Example: 'nova.api.ec2.cloud:nova.notifier.api.notify_decorator'

    Parameters of the decorator is as follows.
    (See nova.notifier.api.notify_decorator)

    name - name of the function
    function - object of the function
    """
    # If FLAGS.monkey_patch is not True, this function do nothing.
    if not FLAGS.monkey_patch:
        return
    # Get list of modules and decorators
    for module_and_decorator in FLAGS.monkey_patch_modules:
        module, decorator_name = module_and_decorator.split(':')
        # import decorator function
        decorator = import_class(decorator_name)
        __import__(module)
        # Retrieve module information using pyclbr
        module_data = pyclbr.readmodule_ex(module)
        for key in module_data.keys():
            # set the decorator for the class methods
            if isinstance(module_data[key], pyclbr.Class):
                clz = import_class("%s.%s" % (module, key))
                for method, func in inspect.getmembers(clz, inspect.ismethod):
                    setattr(clz, method,
                        decorator("%s.%s.%s" % (module, key, method), func))
            # set the decorator for the function
            if isinstance(module_data[key], pyclbr.Function):
                func = import_class("%s.%s" % (module, key))
                setattr(sys.modules[module], key,
                    decorator("%s.%s" % (module, key), func))


def default_flagfile(filename='synaps.conf', args=None):
    if args is None:
        args = sys.argv
    for arg in args:
        if arg.find('flagfile') != -1:
            return arg[arg.index('flagfile') + len('flagfile') + 1:]
    else:
        if not os.path.isabs(filename):
            # turn relative filename into an absolute path
            script_dir = os.path.dirname(inspect.stack()[-1][1])
            filename = os.path.abspath(os.path.join(script_dir, filename))
        if not os.path.exists(filename):
            filename = "./synaps.conf"
            if not os.path.exists(filename):
                filename = '/etc/synaps/synaps.conf'
        if os.path.exists(filename):
            flagfile = '--flagfile=%s' % filename
            args.insert(1, flagfile)
            return filename
                
def find_config(config_path):
    """Find a configuration file using the given hint.

    :param config_path: Full or relative path to the config.
    :returns: Full path of the config, if it exists.
    :raises: `synaps.exception.ConfigNotFound`

    """
    possible_locations = [
        config_path,
        os.path.join(FLAGS.state_path, "etc", "synaps", config_path),
        os.path.join(FLAGS.state_path, "etc", config_path),
        os.path.join(FLAGS.state_path, config_path),
        "/etc/synaps/%s" % config_path,
    ]

    for path in possible_locations:
        if os.path.exists(path):
            return os.path.abspath(path)

    raise exception.ConfigNotFound(path=os.path.abspath(config_path))     

def cleanup_file_locks():
    """clean up stale locks left behind by process failures

    The lockfile module, used by @synchronized, can leave stale lockfiles
    behind after process failure. These locks can cause process hangs
    at startup, when a process deadlocks on a lock which will never
    be unlocked.

    Intended to be called at service startup.

    """

    # NOTE(mikeyp) this routine incorporates some internal knowledge
    #              from the lockfile module, and this logic really
    #              should be part of that module.
    #
    # cleanup logic:
    # 1) look for the lockfile modules's 'sentinel' files, of the form
    #    hostname.[thread-.*]-pid, extract the pid.
    #    if pid doesn't match a running process, delete the file since
    #    it's from a dead process.
    # 2) check for the actual lockfiles. if lockfile exists with linkcount
    #    of 1, it's bogus, so delete it. A link count >= 2 indicates that
    #    there are probably sentinels still linked to it from active
    #    processes.  This check isn't perfect, but there is no way to
    #    reliably tell which sentinels refer to which lock in the
    #    lockfile implementation.

    if  FLAGS.disable_process_locking:
        return

    hostname = socket.gethostname()
    sentinel_re = hostname + r'\..*-(\d+$)'
    lockfile_re = r'synaps-.*\.lock'
    files = os.listdir(FLAGS.lock_path)

    # cleanup sentinels
    for filename in files:
        match = re.match(sentinel_re, filename)
        if match is None:
            continue
        pid = match.group(1)
        LOG.debug(_('Found sentinel %(filename)s for pid %(pid)s' % 
                    {'filename': filename, 'pid': pid}))
        if not os.path.exists(os.path.join('/proc', pid)):
            delete_if_exists(os.path.join(FLAGS.lock_path, filename))
            LOG.debug(_('Cleaned sentinel %(filename)s for pid %(pid)s' % 
                        {'filename': filename, 'pid': pid}))

    # cleanup lock files
    for filename in files:
        match = re.match(lockfile_re, filename)
        if match is None:
            continue
        try:
            stat_info = os.stat(os.path.join(FLAGS.lock_path, filename))
        except OSError as (errno, strerror):
            if errno == 2:  # doesn't exist
                continue
            else:
                raise
        msg = _('Found lockfile %(file)s with link count %(count)d' % 
                {'file': filename, 'count': stat_info.st_nlink})
        LOG.debug(msg)
        if stat_info.st_nlink == 1:
            delete_if_exists(os.path.join(FLAGS.lock_path, filename))
            msg = _('Cleaned lockfile %(file)s with link count %(count)d' % 
                    {'file': filename, 'count': stat_info.st_nlink})
            LOG.debug(msg)
            
def delete_if_exists(pathname):
    """delete a file, but ignore file not found error"""

    try:
        os.unlink(pathname)
    except OSError as (errno, strerror):
        if errno == 2:  # doesn't exist
            return
        else:
            raise                       

def execute(*cmd, **kwargs):
    """
    Helper method to execute command with optional retry.

    :cmd                Passed to subprocess.Popen.
    :process_input      Send to opened process.
    :check_exit_code    Defaults to 0. Raise exception.ProcessExecutionError
                        unless program exits with this code.
    :delay_on_retry     True | False. Defaults to True. If set to True, wait a
                        short amount of time before retrying.
    :attempts           How many times to retry cmd.
    :run_as_root        True | False. Defaults to False. If set to True,
                        the command is prefixed by the command specified
                        in the root_helper FLAG.

    :raises exception.Error on receiving unknown arguments
    :raises exception.ProcessExecutionError
    """

    process_input = kwargs.pop('process_input', None)
    check_exit_code = kwargs.pop('check_exit_code', 0)
    delay_on_retry = kwargs.pop('delay_on_retry', True)
    attempts = kwargs.pop('attempts', 1)
    run_as_root = kwargs.pop('run_as_root', False)
    if len(kwargs):
        raise exception.Error(_('Got unknown keyword args '
                                'to utils.execute: %r') % kwargs)

    if run_as_root:
        cmd = shlex.split(FLAGS.root_helper) + list(cmd)
    cmd = map(str, cmd)

    while attempts > 0:
        attempts -= 1
        try:
            LOG.debug(_('Running cmd (subprocess): %s'), ' '.join(cmd))
            _PIPE = -1 #(subprocess.PIPE)  # pylint: disable=E1101
            obj = subprocess.Popen(cmd,
                                   stdin=_PIPE,
                                   stdout=_PIPE,
                                   stderr=_PIPE,
                                   close_fds=True)
            result = None
            if process_input is not None:
                result = obj.communicate(process_input)
            else:
                result = obj.communicate()
            obj.stdin.close()  # pylint: disable=E1101
            _returncode = obj.returncode  # pylint: disable=E1101
            if _returncode:
                LOG.debug(_('Result was %s') % _returncode)
                if type(check_exit_code) == types.IntType \
                        and _returncode != check_exit_code:
                    (stdout, stderr) = result
                    raise exception.ProcessExecutionError(
                            exit_code=_returncode,
                            stdout=stdout,
                            stderr=stderr,
                            cmd=' '.join(cmd))
            return result
        except exception.ProcessExecutionError:
            if not attempts:
                raise
            else:
                LOG.debug(_('%r failed. Retrying.'), cmd)
                if delay_on_retry:
                    greenthread.sleep(random.randint(20, 200) / 100.0)
        finally:
            # NOTE(termie): this appears to be necessary to let the subprocess
            #               call clean something up in between calls, without
            #               it two execute calls in a row hangs the second one
            greenthread.sleep(0)


def extract_member_list(aws_list, key='member'):
    """
    
    ex) if key is 'member', it will convert from
    
    {'member': {'1': 'something1',
                '2': 'something2',
                '3': 'something3'}}
    
    to            
    
    ['something1', 'something2', 'something3']
    """
    if not aws_list: 
        return []
    return OrderedDict(aws_list[key]).values()

def extract_member_dict(aws_dict, key='member'):
    """
    it will convert from

    {'member': {'1': {'name': u'member1', 'value': u'value1'}},
               {'2': {'name': u'member2', 'value': u'value2'}}}

    to
    
    {u'member1': u'value1', u'member2': u'value2'}
    
    this is useful for processing dimension.
    """
    if not aws_dict:
        return {}
    members = extract_member_list(aws_dict, key)
    member_list = [(member['name'], member['value']) for member in members]
    return dict(member_list)

def dict_to_aws(pydict):
    return [{'name':k, 'value':v} for k, v in pydict.iteritems()]

def datetime_to_timestamp(dt):
    if isinstance(dt, datetime.datetime):
        return calendar.timegm(dt.utctimetuple())
    return dt

def abspath(s):
    return os.path.join(os.path.dirname(__file__), s)

       

def parse_server_string(server_str):
    """
    Parses the given server_string and returns a list of host and port.
    If it's not a combination of host part and port, the port element
    is a null string. If the input is invalid expression, return a null
    list.
    """
    try:
        # First of all, exclude pure IPv6 address (w/o port).
        if netaddr.valid_ipv6(server_str):
            return (server_str, '')

        # Next, check if this is IPv6 address with a port number combination.
        if server_str.find("]:") != -1:
            (address, port) = server_str.replace('[', '', 1).split(']:')
            return (address, port)

        # Third, check if this is a combination of an address and a port
        if server_str.find(':') == -1:
            return (server_str, '')

        # This must be a combination of an address and a port
        (address, port) = server_str.split(':')
        return (address, port)

    except Exception:
        LOG.debug(_('Invalid server_string: %s' % server_str))
        return ('', '')
    
def import_object(import_str):
    """Returns an object including a module or module and class."""
    try:
        __import__(import_str)
        return sys.modules[import_str]
    except ImportError:
        cls = import_class(import_str)
        return cls()

def utcnow_ts():
    """Timestamp version of our utcnow function."""
    return time.mktime(utcnow().timetuple())    

def isotime(at=None):
    """Returns iso formatted utcnow."""
    return strtime(at, ISO_TIME_FORMAT)

@contextlib.contextmanager
def tempdir(**kwargs):
    tmpdir = tempfile.mkdtemp(**kwargs)
    try:
        yield tmpdir
    finally:
        try:
            shutil.rmtree(tmpdir)
        except OSError, e:
            LOG.debug(_('Could not remove tmpdir: %s'), str(e))
            
def strcmp_const_time(s1, s2):
    """Constant-time string comparison.

    :params s1: the first string
    :params s2: the second string

    :return: True if the strings are equal.

    This function takes two strings and compares them.  It is intended to be
    used when doing a comparison for authentication purposes to help guard
    against timing attacks.
    """
    if len(s1) != len(s2):
        return False
    result = 0
    for (a, b) in zip(s1, s2):
        result |= ord(a) ^ ord(b)
    return result == 0            

def prefix_end(buf):
    lastord = ord(buf[-1])
    return buf[:-1] + unichr(lastord + 1)

def xhtml_escape(value):
    """Escapes a string so it is valid within XML or XHTML.

    """
    return saxutils.escape(value, {'"': '&quot;', "'": '&apos;'})

def get_python_novaclient():
    nc = client.Client(FLAGS.get('admin_user'), 
                       FLAGS.get('admin_password'), 
                       FLAGS.get('admin_tenant_name'), 
                       auth_url=FLAGS.get('nova_auth_url'),
                       endpoint_type='internalURL')
    return nc


def generate_metric_key(project_id, namespace, metric_name, dimensions):
    if type(dimensions) is not str:
        dimensions = pack_dimensions(dimensions)
    elements = map(repr, [project_id, namespace, metric_name, dimensions])
    metric_str = " /SEP/ ".join(elements)
    return uuid.uuid5(uuid.NAMESPACE_OID, metric_str)


def pack_dimensions(dimensions):
    return json.dumps(OrderedDict(sorted(dimensions.items())))