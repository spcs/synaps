# Copyright 2012 Samsung SDS
# All Rights Reserved.

import eventlet
import eventlet.wsgi
import webob
import webob.dec
import json

from synaps import flags
from synaps import log as logging
from synaps import wsgi
from synaps import context
from synaps import utils
from synaps import exception
from synaps.api.cloudwatch import faults
from synaps.api.cloudwatch import apirequest
from synaps.openstack.common import cfg

LOG = logging.getLogger(__name__)

cloudwatch_opts = [
    cfg.IntOpt('lockout_attempts',
               default=5,
               help='Number of failed auths before lockout.'),
    cfg.IntOpt('lockout_minutes',
               default=15,
               help='Number of minutes to lockout if triggered.'),
    cfg.IntOpt('lockout_window',
               default=15,
               help='Number of minutes for lockout window.'),
#    cfg.StrOpt('keystone_ec2_url',
#               default='http://localhost:5000/v2.0/ec2tokens',
#               help='URL to get token from ec2 request.'),
    ]

FLAGS = flags.FLAGS
FLAGS.register_opts(cloudwatch_opts)
flags.DECLARE('use_forwarded_for', 'synaps.api.auth')

## Fault Wrapper around all CloudWatch requests ##
class FaultWrapper(wsgi.Middleware):
    """Calls the middleware stack, captures any exceptions into faults."""

    @webob.dec.wsgify(RequestClass=webob.Request)
    def __call__(self, req):
        try:
            return req.get_response(self.application)
        except Exception as ex:
            LOG.exception(_("FaultWrapper: %s"), unicode(ex))
            return faults.Fault(webob.exc.HTTPInternalServerError())
        

class RequestLogging(wsgi.Middleware):
    """Access-Log akin logging for all Synaps API requests."""

    @webob.dec.wsgify(RequestClass=webob.Request)
    def __call__(self, req):
        start = utils.utcnow()
        rv = req.get_response(self.application)
        self.log_request_completion(rv, req, start)
        return rv

    def log_request_completion(self, response, request, start):
        apireq = request.environ.get('cloudwatch.request', None)
        if apireq:
            controller = apireq.controller
            action = apireq.action
        else:
            controller = None
            action = None
        ctxt = request.environ.get('synaps.context', None)
        delta = utils.utcnow() - start
        seconds = delta.seconds
        microseconds = delta.microseconds
        LOG.info(
            "%s.%ss %s %s %s %s:%s %s [%s] %s %s",
            seconds,
            microseconds,
            request.remote_addr,
            request.method,
            "%s%s" % (request.script_name, request.path_info),
            controller,
            action,
            response.status_int,
            request.user_agent,
            request.content_type,
            response.content_type,
            context=ctxt)        

class NoAuth(wsgi.Middleware):
    """Add user:project as 'synaps.context' to WSGI environ."""

    @webob.dec.wsgify(RequestClass=webob.Request)
    def __call__(self, req):
        if 'AWSAccessKeyId' not in req.params:
            raise webob.exc.HTTPBadRequest()
        user_id, _sep, project_id = req.params['AWSAccessKeyId'].partition(':')
        project_id = project_id or user_id
        remote_address = req.remote_addr
        if FLAGS.use_forwarded_for:
            remote_address = req.headers.get('X-Forwarded-For', remote_address)
        ctx = context.RequestContext(user_id,
                                     project_id,
                                     is_admin=True,
                                     remote_address=remote_address)

        req.environ['synaps.context'] = ctx
        return self.application

class Requestify(wsgi.Middleware):

    def __init__(self, app, controller):
        super(Requestify, self).__init__(app)
        self.controller = utils.import_class(controller)()

    @webob.dec.wsgify(RequestClass=webob.Request)
    def __call__(self, req):
        non_args = ['Action', 'Signature', 'AWSAccessKeyId', 'SignatureMethod',
                    'SignatureVersion', 'Version', 'Timestamp']
        args = dict(req.params)
        try:
            # Raise KeyError if omitted
            action = req.params['Action']
            # Fix bug lp:720157 for older (version 1) clients
            version = req.params['SignatureVersion']
            if int(version) == 1:
                non_args.remove('SignatureMethod')
                if 'SignatureMethod' in args:
                    args.pop('SignatureMethod')
            for non_arg in non_args:
                # Remove, but raise KeyError if omitted
                args.pop(non_arg)
        except KeyError, e:
            raise webob.exc.HTTPBadRequest()

        LOG.debug(_('action: %s'), action)
        for key, value in args.items():
            LOG.debug(_('arg: %(key)s\t\tval: %(value)s') % locals())

        # Success!
        api_request = apirequest.APIRequest(self.controller, action,
                                            req.params['Version'], args)
        req.environ['cloudwatch.request'] = api_request
        return self.application

class Authorizer(wsgi.Middleware):

    """Authorize an Cloudwatch API request.

    Return a 401 if cloudwatch.controller and cloudwatch.action in WSGI environ 
    may not be executed in cloudwatch.context.
    """

    def __init__(self, application):
        super(Authorizer, self).__init__(application)
        self.action_roles = {
            'MonitorController': {
                 'PutMetricData': ['all'], #'netadmin'],
                 'GetMetricStatistics': ['all'],
                 'ListMetrics':['all'],
#                'DescribeAvailabilityZones': ['all'],
#                'DescribeRegions': ['all'],
#                'DescribeSnapshots': ['all'],
#                'DescribeKeyPairs': ['all'],
#                'CreateKeyPair': ['all'],
#                'DeleteKeyPair': ['all'],
#                'DescribeSecurityGroups': ['all'],
#                'ImportKeyPair': ['all'],
#                'AuthorizeSecurityGroupIngress': ['netadmin'],
#                'RevokeSecurityGroupIngress': ['netadmin'],
#                'CreateSecurityGroup': ['netadmin'],
#                'DeleteSecurityGroup': ['netadmin'],
#                'GetConsoleOutput': ['projectmanager', 'sysadmin'],
#                'DescribeVolumes': ['projectmanager', 'sysadmin'],
#                'CreateVolume': ['projectmanager', 'sysadmin'],
#                'AttachVolume': ['projectmanager', 'sysadmin'],
#                'DetachVolume': ['projectmanager', 'sysadmin'],
#                'DescribeInstances': ['all'],
#                'DescribeAddresses': ['all'],
#                'AllocateAddress': ['netadmin'],
#                'ReleaseAddress': ['netadmin'],
#                'AssociateAddress': ['netadmin'],
#                'DisassociateAddress': ['netadmin'],
#                'RunInstances': ['projectmanager', 'sysadmin'],
#                'TerminateInstances': ['projectmanager', 'sysadmin'],
#                'RebootInstances': ['projectmanager', 'sysadmin'],
#                'UpdateInstance': ['projectmanager', 'sysadmin'],
#                'StartInstances': ['projectmanager', 'sysadmin'],
#                'StopInstances': ['projectmanager', 'sysadmin'],
#                'DeleteVolume': ['projectmanager', 'sysadmin'],
#                'DescribeImages': ['all'],
#                'DeregisterImage': ['projectmanager', 'sysadmin'],
#                'RegisterImage': ['projectmanager', 'sysadmin'],
#                'DescribeImageAttribute': ['all'],
#                'ModifyImageAttribute': ['projectmanager', 'sysadmin'],
#                'UpdateImage': ['projectmanager', 'sysadmin'],
#                'CreateImage': ['projectmanager', 'sysadmin'],
            },
            'AdminController': {
                # All actions have the same permission: ['none'] (the default)
                # superusers will be allowed to run them
                # all others will get HTTPUnauthorized.
            },
        }

    @webob.dec.wsgify(RequestClass=webob.Request)
    def __call__(self, req):
        context = req.environ['synaps.context']
        controller = req.environ['cloudwatch.request'].controller.__class__.__name__
        action = req.environ['cloudwatch.request'].action
        allowed_roles = self.action_roles[controller].get(action, ['none'])
        if self._matches_any_role(context, allowed_roles):
            return self.application
        else:
            LOG.audit(_('Unauthorized request for controller=%(controller)s '
                        'and action=%(action)s') % locals(), context=context)
            raise webob.exc.HTTPUnauthorized()

    def _matches_any_role(self, context, roles):
        """Return True if any role in roles is allowed in context."""
        if context.is_admin:
            return True
        if 'all' in roles:
            return True
        if 'none' in roles:
            return False
        return any(role in context.roles for role in roles)


class Executor(wsgi.Application):
    @webob.dec.wsgify(RequestClass=webob.Request)
    def __call__(self, req):
        api_request = req.environ['cloudwatch.request']
        context = req.environ['synaps.context']
        result = None
        
        try:
            result = api_request.invoke(context)
        except exception.CloudwatchAPIError as ex:
            LOG.exception(_('CloudwatchApiError raised: %s'), unicode(ex),
                          context=context)
            if ex.code:
                return self._error(req, context, ex.code, unicode(ex))
            else:
                return self._error(req, context, type(ex).__name__,
                                   unicode(ex))
        else:
            resp = webob.Response()
            resp.status = 200
            resp.headers['Content-Type'] = 'text/xml'
            resp.body = str(result)
            return resp                            

    def _error(self, req, context, code, message):
        LOG.error("%s: %s", code, message, context=context)
        resp = webob.Response()
        resp.status = 400
        resp.headers['Content-Type'] = 'text/xml'
        resp.body = str('<?xml version="1.0"?>\n'
                         '<Response><Errors><Error><Code>%s</Code>'
                         '<Message>%s</Message></Error></Errors>'
                         '<RequestID>%s</RequestID></Response>' % 
                         (utils.utf8(code), utils.utf8(message),
                         utils.utf8(context.request_id)))
        return resp
