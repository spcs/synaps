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

SYNAPS_VERSION = ['12', '09', 'b6']
YEAR, COUNT, REVISION = SYNAPS_VERSION
FINAL = True   # This becomes true at Release Candidate time


def canonical_version_string():
    return '.'.join(filter(None, SYNAPS_VERSION))


def version_string():
    if FINAL:
        return canonical_version_string()
    else:
        return '%s-dev' % (canonical_version_string(),)


def vcs_version_string():
    return 'LOCALBRANCH:LOCALREVISION'


def version_string_with_vcs():
    return '%s-%s' % (canonical_version_string(), vcs_version_string())
