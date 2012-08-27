# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 SamsungSDS, Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
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

"""Synaps base exception handling.

Includes decorator for re-raising Synaps-type exceptions.

SHOULD include dedicated exception logging.

"""

import functools
import sys

import webob.exc

from synaps import log as logging

LOG = logging.getLogger(__name__)


class ConvertedException(webob.exc.WSGIHTTPException):
    def __init__(self, code=0, title="", explanation=""):
        self.code = code
        self.title = title
        self.explanation = explanation
        super(ConvertedException, self).__init__()


class ProcessExecutionError(IOError):
    def __init__(self, stdout=None, stderr=None, exit_code=None, cmd=None,
                 description=None):
        self.exit_code = exit_code
        self.stderr = stderr
        self.stdout = stdout
        self.cmd = cmd
        self.description = description

        if description is None:
            description = _('Unexpected error while running command.')
        if exit_code is None:
            exit_code = '-'
        message = _('%(description)s\nCommand: %(cmd)s\n'
                    'Exit code: %(exit_code)s\nStdout: %(stdout)r\n'
                    'Stderr: %(stderr)r') % locals()
        IOError.__init__(self, message)


class Error(Exception):
    pass


class CloudwatchAPIError(Error):
    def __init__(self, message='Unknown', code=None):
        self.msg = message
        self.code = code
        if code:
            outstr = '%s: %s' % (code, message)
        else:
            outstr = '%s' % message
        super(CloudwatchAPIError, self).__init__(outstr)


class DBError(Error):
    """Wraps an implementation specific exception."""
    def __init__(self, inner_exception=None):
        self.inner_exception = inner_exception
        super(DBError, self).__init__(str(inner_exception))


def wrap_db_error(f):
    def _wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception, e:
            LOG.exception(_('DB exception wrapped.'))
            raise DBError(e)
    _wrap.func_name = f.func_name
    return _wrap


def wrap_exception(notifier=None, publisher_id=None, event_type=None,
                   level=None):
    """This decorator wraps a method to catch any exceptions that may
    get thrown. It logs the exception as well as optionally sending
    it to the notification system.
    """
    # TODO(sandy): Find a way to import nova.notifier.api so we don't have
    # to pass it in as a parameter. Otherwise we get a cyclic import of
    # nova.notifier.api -> nova.utils -> nova.exception :(
    # TODO(johannes): Also, it would be nice to use
    # utils.save_and_reraise_exception() without an import loop
    def inner(f):
        def wrapped(*args, **kw):
            try:
                return f(*args, **kw)
            except Exception, e:
                # Save exception since it can be clobbered during processing
                # below before we can re-raise
                exc_info = sys.exc_info()

                if notifier:
                    payload = dict(args=args, exception=e)
                    payload.update(kw)

                    # Use a temp vars so we don't shadow
                    # our outer definitions.
                    temp_level = level
                    if not temp_level:
                        temp_level = notifier.ERROR

                    temp_type = event_type
                    if not temp_type:
                        # If f has multiple decorators, they must use
                        # functools.wraps to ensure the name is
                        # propagated.
                        temp_type = f.__name__

                    notifier.notify(publisher_id, temp_type, temp_level,
                                    payload)

                # re-raise original exception since it may have been clobbered
                raise exc_info[0], exc_info[1], exc_info[2]

        return functools.wraps(f)(wrapped)
    return inner


class SynapsException(Exception):
    """Base Synaps Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.

    """
    message = _("An unknown exception occurred.")

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            try:
                message = self.message % kwargs

            except Exception as e:
                # at least get the core message out if something happened
                message = self.message

        super(SynapsException, self).__init__(message)


class DecryptionFailure(SynapsException):
    message = _("Failed to decrypt text")


class NotAuthorized(SynapsException):
    message = _("Not authorized.")
    code = 403


class AdminRequired(NotAuthorized):
    message = _("User does not have admin privileges")
    code = 403
    

class Invalid(SynapsException):
    message = _("Unacceptable parameters.")
    code = 400


class InvalidKeypair(Invalid):
    message = _("Keypair data is invalid")


class InvalidRequest(Invalid):
    message = _("The request is invalid.")


class InvalidNextToken(Invalid):
    message = _("The next token is invalid UUID format")


class InvalidSignature(Invalid):
    message = _("Invalid signature %(signature)s for user %(user)s.")


class InvalidFormat(Invalid):
    message = _("Invalid json format")

# Cannot be templated as the error syntax varies.
# msg needs to be constructed when raised.
class InvalidParameterValue(Invalid):
    message = _("%(err)s")


class ResourceNotFound(SynapsException):
    message = _("Resource could not be found.")
    code = 404


class ProjectNotFound(ResourceNotFound):
    message = _("Project %(project_id)s could not be found.")


class ProjectMembershipNotFound(ResourceNotFound):
    message = _("User %(user_id)s is not a member of project %(project_id)s.")


class UserRoleNotFound(ResourceNotFound):
    message = _("Role %(role_id)s could not be found.")


class AccessKeyNotFound(ResourceNotFound):
    message = _("Access Key %(access_key)s could not be found.")


class ClassNotFound(ResourceNotFound):
    message = _("Class %(class_name)s could not be found: %(exception)s")


class NotAllowed(SynapsException):
    message = _("Action not allowed.")


class GlobalRoleNotAllowed(NotAllowed):
    message = _("Unable to use global role %(role_id)s")


class ConfigNotFound(ResourceNotFound):
    message = _("Could not find config at %(path)s")


class PasteAppNotFound(ResourceNotFound):
    message = _("Could not load paste app '%(name)s' from %(path)s")


# Synaps custom exceptions 
class RpcInvokeException(SynapsException):
    message = _("Unable to invoke RPC")
