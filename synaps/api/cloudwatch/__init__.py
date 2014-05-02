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

import eventlet
import eventlet.wsgi
from eventlet.green import httplib
import webob
import webob.dec
import json
import urlparse
import hashlib

from synaps import flags
from synaps import log as logging
from synaps import wsgi
from synaps import context
from synaps import utils
from synaps import exception
from synaps.api.cloudwatch import faults
from synaps.api.cloudwatch import apirequest
from synaps.auth import manager
from synaps.openstack.common import cfg
from synaps.openstack.common import jsonutils

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
    ]

FLAGS = flags.FLAGS
FLAGS.register_opts(cloudwatch_opts)
flags.DECLARE('use_forwarded_for', 'synaps.api.auth')

def cloudwatch_error(req, request_id, code, message):
    """Helper to send an cloudwatch_compatible error"""
    LOG.error(_('%(code)s: %(message)s') % locals())
    resp = webob.Response()
    resp.status = code
    resp.headers['Content-Type'] = 'text/xml'
    resp.body = str('<?xml version="1.0"?>\n'
                    '<ErrorResponse xmlns="http://monitoring.amazonaws.com/doc/2010-08-01/">'
                    '<Error><Code>%s</Code><Message>%s</Message></Error>'
                    '<RequestId>%s</RequestId></ErrorResponse>' % 
                    (code, utils.utf8(message), utils.utf8(request_id)))
    return resp

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


class EC2KeystoneAuth(wsgi.Middleware):
    """Authenticate an EC2 request with keystone and convert to context."""

    @webob.dec.wsgify(RequestClass=webob.Request)
    def __call__(self, req):
        request_id = context.generate_request_id()
        signature = req.params.get('Signature')
        if not signature:
            msg = _("Signature not provided")
            return faults.ec2_error_response(request_id, "Unauthorized", msg,
                                             status=400)
        access = req.params.get('AWSAccessKeyId')
        if not access:
            msg = _("Access key not provided")
            return faults.ec2_error_response(request_id, "Unauthorized", msg,
                                             status=400)

        # Make a copy of args for authentication and signature verification.
        auth_params = dict(req.params)
        # Not part of authentication args
        auth_params.pop('Signature')

        cred_dict = {
            'access': access,
            'signature': signature,
            'host': req.host,
            'verb': req.method,
            'path': req.path,
            'params': auth_params,
        }
        if "ec2" in FLAGS.keystone_ec2_url:
            creds = {'ec2Credentials': cred_dict}
        else:
            creds = {'auth': {'OS-KSEC2:ec2Credentials': cred_dict}}
        creds_json = jsonutils.dumps(creds)
        headers = {'Content-Type': 'application/json'}

        o = urlparse.urlparse(FLAGS.keystone_ec2_url)
        if o.scheme == "http":
            conn = httplib.HTTPConnection(o.netloc)
        else:
            conn = httplib.HTTPSConnection(o.netloc)
        conn.request('POST', o.path, body=creds_json, headers=headers)
        response = conn.getresponse()
        data = response.read()
        if response.status != 200:
            if response.status == 401:
                msg = response.reason
            else:
                msg = _("Failure communicating with keystone")
            return faults.ec2_error_response(request_id, "Unauthorized", msg,
                                             status=400)
        result = jsonutils.loads(data)
        conn.close()

        try:
            token_id = result['access']['token']['id']
            user_id = result['access']['user']['id']
            project_id = result['access']['token']['tenant']['id']
            user_name = result['access']['user'].get('name')
            project_name = result['access']['token']['tenant'].get('name')
            roles = [role['name'] for role
                     in result['access']['user']['roles']]
        except (AttributeError, KeyError) as e:
            LOG.exception(_("Keystone failure: %s") % e)
            msg = _("Failure communicating with keystone")
            return faults.ec2_error_response(request_id, "Unauthorized", msg,
                                             status=400)

        remote_address = req.remote_addr
        if FLAGS.use_forwarded_for:
            remote_address = req.headers.get('X-Forwarded-For',
                                             remote_address)

        catalog = result['access']['serviceCatalog']
        ctxt = context.RequestContext(user_id,
                                      project_id,
                                      #user_name=user_name,
                                      #project_name=project_name,
                                      roles=roles,
                                      auth_token=token_id,
                                      remote_address=remote_address)
                                      #service_catalog=catalog)

        req.environ['synaps.context'] = ctxt

        return self.application


class Authenticate(wsgi.Middleware):
    """Authenticate an CloudWatch request and add 'synaps.context' to
    WSGI environ."""

    def _get_signature(self, req):
        """
        Extract the signature from the request, this can be a get/post
        variable or for v4 also in a header called 'Authorization'
        - params['Signature'] == version 0,1,2,3
        - params['X-Amz-Signature'] == version 4
        - header 'Authorization' == version 4
        """
        sig = req.params.get('Signature') or req.params.get('X-Amz-Signature')
        if sig is None and 'Authorization' in req.headers:
            auth_str = req.headers['Authorization']
            sig = auth_str.partition("Signature=")[2].split(',')[0]

        return sig
    
    def _get_access(self, req):
        """
        Extract the access key identifier, for v 0/1/2/3 this is passed
        as the AccessKeyId parameter, for version4 it is either and
        X-Amz-Credential parameter or a Credential= field in the
        'Authorization' header string
        """
        access = req.params.get('AWSAccessKeyId')
        if access is None:
            cred_param = req.params.get('X-Amz-Credential')
            if cred_param:
                access = cred_param.split("/")[0]

        if access is None and 'Authorization' in req.headers:
            auth_str = req.headers['Authorization']
            cred_str = auth_str.partition("Credential=")[2].split(',')[0]
            access = cred_str.split("/")[0]

        return access
    
    @webob.dec.wsgify(RequestClass=webob.Request)
    def __call__(self, req):
        request_id = context.generate_request_id()
        # Read request signature and access id.
        signature = self._get_signature(req)
        access = self._get_access(req)
        
        if not (signature or access): 
            msg = _("Access key or signature not provided")
            return faults.ec2_error_response(request_id, "Unauthorized", msg,
                                             status=400)

        # Make a copy of args for authentication and signature verification.
        auth_params = dict(req.GET)
        # Not part of authentication args
        auth_params.pop('Signature', None)
        
        # Authenticate the request.
        # AWS v4 authentication requires a hash of the body
        body_hash = hashlib.sha256(req.body).hexdigest()
        creds = {'ec2Credentials': {'access': access,
                                    'signature': signature,
                                    'host': req.host,
                                    'verb': req.method,
                                    'path': req.path,
                                    'params': auth_params,
                                    'headers': req.headers,
                                    'body_hash': body_hash
                                    }}
        LOG.debug("creds: %s", creds)

        # Authenticate the request.
        authman = manager.AuthManager()
        try:
            (user, project) = authman.authenticate(
                    access,
                    signature,
                    auth_params,
                    req.method,
                    req.host,
                    req.path,
                    headers=req.headers,
                    body_hash=body_hash)
        # Be explicit for what exceptions are 403, the rest bubble as 500
        except (exception.ResourceNotFound, exception.NotAuthorized,
                exception.InvalidSignature) as ex:
            LOG.audit(_("Authentication Failure: %s"), unicode(ex))
            msg = _("Authentication Failure")
            return faults.ec2_error_response(request_id, "Unauthorized", msg,
                                             status=400)

        # Authenticated!
        remote_address = req.remote_addr
        if FLAGS.use_forwarded_for:
            remote_address = req.headers.get('X-Forwarded-For', remote_address)
        roles = authman.get_active_roles(user, project)
        ctxt = context.RequestContext(user_id=user.id,
                                      project_id=project.id,
                                      is_admin=user.is_admin(),
                                      roles=roles,
                                      remote_address=remote_address)
        req.environ['synaps.context'] = ctxt
        uname = user.name
        pname = project.name
        msg = _('Authenticated Request For %(uname)s:%(pname)s)') % locals()
        LOG.audit(msg, context=req.environ['synaps.context'])
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
            version = req.params.get('SignatureVersion', None)
            if version and int(version) == 1:
                non_args.remove('SignatureMethod')
                if 'SignatureMethod' in args:
                    args.pop('SignatureMethod', None)
            for non_arg in non_args:
                # Remove, but raise KeyError if omitted
                args.pop(non_arg, None)
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
                 'DeleteAlarms':['all'],
                 'DescribeAlarmHistory':['all'],
                 'DescribeAlarms':['all'],
                 'DescribeAlarmsForMetric':['all'],
                 'DisableAlarmActions':['all'],
                 'EnableAlarmActions':['all'],
                 'GetMetricStatistics': ['all'],
                 'ListMetrics':['all'],
                 'PutMetricAlarm':['all'],
                 'PutMetricData':['all'],
                 'SetAlarmState':['all'],
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
        context = req.environ['synaps.context']
        request_id = context.request_id
        api_request = req.environ['cloudwatch.request']
        result = None
        
        try:
            result = api_request.invoke(context)
        except (exception.CloudwatchAPIError, exception.SynapsException) as ex:
            if ex.code:
                return cloudwatch_error(req, request_id, ex.code, unicode(ex))
            else:
                return cloudwatch_error(req, request_id, type(ex).__name__,
                                        unicode(ex))            
        except Exception as ex:
            env = req.environ.copy()
            for k in env.keys():
                if not isinstance(env[k], basestring):
                    env.pop(k)

            LOG.exception(_('Unexpected error raised: %s'), unicode(ex))
            LOG.error(_('Environment: %s') % utils.dumps(env))
            return cloudwatch_error(req, request_id, 500,
                                    _('An unknown error has occurred. '
                                      'Please try your request again.'))                        
        else:
            resp = webob.Response()
            resp.status = 200
            resp.headers['Content-Type'] = 'text/xml'
            resp.body = str(result)
            return resp                            
