# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Samsung SDS
# All Rights Reserved.

SYNAPS_VERSION = ['2012', '05', '28']
YEAR, COUNT, REVISION = SYNAPS_VERSION
FINAL = False   # This becomes true at Release Candidate time


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
