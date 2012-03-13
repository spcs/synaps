# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Samsung SDS
# All Rights Reserved.


"""Greenthread local storage of variables using weak references"""

import weakref

from eventlet import corolocal


class WeakLocal(corolocal.local):
    def __getattribute__(self, attr):
        rval = corolocal.local.__getattribute__(self, attr)
        if rval:
            rval = rval()
        return rval

    def __setattr__(self, attr, value):
        value = weakref.ref(value)
        return corolocal.local.__setattr__(self, attr, value)


store = WeakLocal()
