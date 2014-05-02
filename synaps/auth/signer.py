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
#
# PORTIONS OF THIS FILE ARE FROM:
# http://code.google.com/p/boto
# Copyright (c) 2006-2009 Mitch Garnaat http://garnaat.org/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.


"""
Utility class for parsing signed AMI manifests.
"""

import base64
import hashlib
import hmac
import re
import six
from six.moves import urllib

# NOTE(vish): for new boto
import boto
# NOTE(vish): for old boto
import boto.utils

from synaps import log as logging
from synaps.exception import Error


LOG = logging.getLogger(__name__)


class Signer(object):
    """Hacked up code from boto/connection.py"""

    def __init__(self, secret_key):
        self.hmac = hmac.new(secret_key, digestmod=hashlib.sha1)
        if hashlib.sha256:
            self.hmac_256 = hmac.new(secret_key, digestmod=hashlib.sha256)

    def s3_authorization(self, headers, verb, path):
        """Generate S3 authorization string."""
        c_string = boto.utils.canonical_string(verb, path, headers)
        hmac_copy = self.hmac.copy()
        hmac_copy.update(c_string)
        b64_hmac = base64.encodestring(hmac_copy.digest()).strip()
        return b64_hmac

    def generate(self, params, verb, server_string, path):
        """Generate auth string according to what SignatureVersion is given."""
        if params['SignatureVersion'] == '0':
            return self._calc_signature_0(params)
        if params['SignatureVersion'] == '1':
            return self._calc_signature_1(params)
        if params['SignatureVersion'] == '2':
            return self._calc_signature_2(params, verb, server_string, path)
        raise Error('Unknown Signature Version: %s' %
                    params['SignatureVersion'])

    @staticmethod
    def _get_utf8_value(value):
        """Get the UTF8-encoded version of a value."""
        if not isinstance(value, str) and not isinstance(value, unicode):
            value = str(value)
        if isinstance(value, unicode):
            return value.encode('utf-8')
        else:
            return value

    def _calc_signature_0(self, params):
        """Generate AWS signature version 0 string."""
        s = params['Action'] + params['Timestamp']
        self.hmac.update(s)
        keys = params.keys()
        keys.sort(cmp=lambda x, y: cmp(x.lower(), y.lower()))
        pairs = []
        for key in keys:
            val = self._get_utf8_value(params[key])
            pairs.append(key + '=' + urllib.quote(val))
        return base64.b64encode(self.hmac.digest())

    def _calc_signature_1(self, params):
        """Generate AWS signature version 1 string."""
        keys = params.keys()
        keys.sort(cmp=lambda x, y: cmp(x.lower(), y.lower()))
        pairs = []
        for key in keys:
            self.hmac.update(key)
            val = self._get_utf8_value(params[key])
            self.hmac.update(val)
            pairs.append(key + '=' + urllib.quote(val))
        return base64.b64encode(self.hmac.digest())

    def _calc_signature_2(self, params, verb, server_string, path):
        """Generate AWS signature version 2 string."""
        LOG.debug('using _calc_signature_2')
        string_to_sign = '%s\n%s\n%s\n' % (verb, server_string, path)
        if self.hmac_256:
            current_hmac = self.hmac_256
            params['SignatureMethod'] = 'HmacSHA256'
        else:
            current_hmac = self.hmac
            params['SignatureMethod'] = 'HmacSHA1'
        keys = params.keys()
        keys.sort()
        pairs = []
        for key in keys:
            val = self._get_utf8_value(params[key])
            val = urllib.quote(val, safe='-_~')
            pairs.append(urllib.quote(key, safe='') + '=' + val)
        qs = '&'.join(pairs)
        LOG.debug('query string: %s', qs)
        string_to_sign += qs
        LOG.debug('string_to_sign: %s', string_to_sign)
        current_hmac.update(string_to_sign)
        b64 = base64.b64encode(current_hmac.digest())
        LOG.debug('len(b64)=%d', len(b64))
        LOG.debug('base64 encoded digest: %s', b64)
        return b64



class Ec2Signer(object):
    """Utility class which adds allows a request to be signed with an AWS style
    signature, which can then be used for authentication via the keystone ec2
    authentication extension.
    """

    def __init__(self, secret_key):
        self.secret_key = secret_key.encode()
        self.hmac = hmac.new(self.secret_key, digestmod=hashlib.sha1)
        if hashlib.sha256:
            self.hmac_256 = hmac.new(self.secret_key, digestmod=hashlib.sha256)

    def _v4_creds(self, credentials):
        """Detect if the credentials are for a v4 signed request, since AWS
        removed the SignatureVersion field from the v4 request spec...

        This expects a dict of the request headers to be passed in the
        credentials dict, since the recommended way to pass v4 creds is
        via the 'Authorization' header
        see http://docs.aws.amazon.com/general/latest/gr/
            sigv4-signed-request-examples.html

        Alternatively X-Amz-Algorithm can be specified as a query parameter,
        and the authentication data can also passed as query parameters.

        Note a hash of the request body is also required in the credentials
        for v4 auth to work in the body_hash key, calculated via:
        hashlib.sha256(req.body).hexdigest()
        """
        try:
            LOG.debug("headers %s", credentials['headers'])
            auth_str = credentials['headers']['Authorization']
            if auth_str.startswith('AWS4-HMAC-SHA256'):
                return True
        except KeyError:
            # Alternatively the Authorization data can be passed via
            # the query params list, check X-Amz-Algorithm=AWS4-HMAC-SHA256
            try:
                if (credentials['params']['X-Amz-Algorithm'] ==
                        'AWS4-HMAC-SHA256'):
                    return True
            except KeyError:
                pass

        return False

    def generate(self, credentials):
        """Generate auth string according to what SignatureVersion is given."""
        LOG.debug("credentials: %s", credentials)
        signature_version = credentials['params'].get('SignatureVersion')
        if signature_version == '0':
            return self._calc_signature_0(credentials['params'])
        if signature_version == '1':
            return self._calc_signature_1(credentials['params'])
        if signature_version == '2':
            return self._calc_signature_2(credentials['params'],
                                          credentials['verb'],
                                          credentials['host'],
                                          credentials['path'])
        if self._v4_creds(credentials):
            return self._calc_signature_4(credentials['params'],
                                          credentials['verb'],
                                          credentials['host'],
                                          credentials['path'],
                                          credentials['headers'],
                                          credentials['body_hash'])

        if signature_version is not None:
            raise Exception('Unknown signature version: %s' %
                            signature_version)
        else:
            raise Exception('Unexpected signature format')

    @staticmethod
    def _get_utf8_value(value):
        """Get the UTF8-encoded version of a value."""
        if not isinstance(value, (six.binary_type, six.text_type)):
            value = str(value)
        if isinstance(value, six.text_type):
            return value.encode('utf-8')
        else:
            return value

    def _calc_signature_0(self, params):
        """Generate AWS signature version 0 string."""
        s = (params['Action'] + params['Timestamp']).encode('utf-8')
        self.hmac.update(s)
        return base64.b64encode(self.hmac.digest()).decode('utf-8')

    def _calc_signature_1(self, params):
        """Generate AWS signature version 1 string."""
        keys = list(params)
        keys.sort(key=six.text_type.lower)
        for key in keys:
            self.hmac.update(key.encode('utf-8'))
            val = self._get_utf8_value(params[key])
            self.hmac.update(val)
        return base64.b64encode(self.hmac.digest()).decode('utf-8')

    @staticmethod
    def _canonical_qs(params):
        """Construct a sorted, correctly encoded query string as required for
        _calc_signature_2 and _calc_signature_4.
        """
        keys = list(params)
        keys.sort()
        pairs = []
        for key in keys:
            val = Ec2Signer._get_utf8_value(params[key])
            val = urllib.parse.quote(val, safe='-_~')
            pairs.append(urllib.parse.quote(key, safe='') + '=' + val)
        qs = '&'.join(pairs)
        return qs

    def _calc_signature_2(self, params, verb, server_string, path):
        """Generate AWS signature version 2 string."""
        string_to_sign = '%s\n%s\n%s\n' % (verb, server_string, path)
        if self.hmac_256:
            current_hmac = self.hmac_256
            params['SignatureMethod'] = 'HmacSHA256'
        else:
            current_hmac = self.hmac
            params['SignatureMethod'] = 'HmacSHA1'
        string_to_sign += self._canonical_qs(params)
        current_hmac.update(string_to_sign.encode('utf-8'))
        b64 = base64.b64encode(current_hmac.digest()).decode('utf-8')
        return b64

    def _calc_signature_4(self, params, verb, server_string, path, headers,
                          body_hash):
        """Generate AWS signature version 4 string."""

        def sign(key, msg):
            return hmac.new(key, self._get_utf8_value(msg),
                            hashlib.sha256).digest()

        def signature_key(datestamp, region_name, service_name):
            """Signature key derivation, see
            http://docs.aws.amazon.com/general/latest/gr/
            signature-v4-examples.html#signature-v4-examples-python
            """
            k_date = sign(self._get_utf8_value(b"AWS4" + self.secret_key),
                          datestamp)
            k_region = sign(k_date, region_name)
            k_service = sign(k_region, service_name)
            k_signing = sign(k_service, "aws4_request")
            return k_signing

        def auth_param(param_name):
            """Get specified auth parameter.

            Provided via one of:
            - the Authorization header
            - the X-Amz-* query parameters
            """
            try:
                auth_str = headers['Authorization']
                param_str = auth_str.partition(
                    '%s=' % param_name)[2].split(',')[0]
            except KeyError:
                param_str = params.get('X-Amz-%s' % param_name)
            return param_str

        def date_param():
            """Get the X-Amz-Date' value, which can be either a header
            or parameter.

            Note AWS supports parsing the Date header also, but this is not
            currently supported here as it will require some format mangling
            So the X-Amz-Date value must be YYYYMMDDTHHMMSSZ format, then it
            can be used to match against the YYYYMMDD format provided in the
            credential scope.
            see:
            http://docs.aws.amazon.com/general/latest/gr/
            sigv4-date-handling.html
            """
            try:
                return headers['X-Amz-Date']
            except KeyError:
                return params.get('X-Amz-Date')

        def canonical_header_str():
            # Get the list of headers to include, from either
            # - the Authorization header (SignedHeaders key)
            # - the X-Amz-SignedHeaders query parameter
            headers_lower = dict((k.lower().strip(), v.strip())
                                 for (k, v) in six.iteritems(headers))

            # Boto versions < 2.9.3 strip the port component of the host:port
            # header, so detect the user-agent via the header and strip the
            # port if we detect an old boto version.  FIXME: remove when all
            # distros package boto >= 2.9.3, this is a transitional workaround
            user_agent = headers_lower.get('user-agent', '')
            strip_port = re.match('Boto/2.[0-9].[0-2]', user_agent)

            header_list = []
            sh_str = auth_param('SignedHeaders')
            for h in sh_str.split(';'):
                if h not in headers_lower:
                    continue

                if h == 'host' and strip_port:
                    header_list.append('%s:%s' %
                                       (h, headers_lower[h].split(':')[0]))
                    continue

                header_list.append('%s:%s' % (h, headers_lower[h]))
            return '\n'.join(header_list) + '\n'

        # Create canonical request:
        # http://docs.aws.amazon.com/general/latest/gr/
        # sigv4-create-canonical-request.html
        # Get parameters and headers in expected string format
        cr = "\n".join((verb.upper(), path,
                        self._canonical_qs(params),
                        canonical_header_str(),
                        auth_param('SignedHeaders'),
                        body_hash))

        # Check the date, reject any request where the X-Amz-Date doesn't
        # match the credential scope
        credential = auth_param('Credential')
        credential_split = credential.split('/')
        credential_scope = '/'.join(credential_split[1:])
        credential_date = credential_split[1]
        param_date = date_param()
        if not param_date.startswith(credential_date):
            raise Exception('Request date mismatch error')

        # Create the string to sign
        # http://docs.aws.amazon.com/general/latest/gr/
        # sigv4-create-string-to-sign.html
        cr = cr.encode('utf-8')
        string_to_sign = '\n'.join(('AWS4-HMAC-SHA256',
                                    param_date,
                                    credential_scope,
                                    hashlib.sha256(cr).hexdigest()))
        
        # Calculate the derived key, this requires a datestamp, region
        # and service, which can be extracted from the credential scope
        (req_region, req_service) = credential_split[2:4]
        s_key = signature_key(credential_date, req_region, req_service)
        # Finally calculate the signature!
        signature = hmac.new(s_key, self._get_utf8_value(string_to_sign),
                             hashlib.sha256).hexdigest()
        return signature



if __name__ == '__main__':
    print Signer('foo').generate({'SignatureMethod': 'HmacSHA256',
                                  'SignatureVersion': '2'},
                                 'get', 'server', '/foo')
