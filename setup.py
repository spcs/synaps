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

import glob
import os

import setuptools
from setuptools.command import sdist
from synaps.openstack.common import setup as common_setup

from setuptools import find_packages
from setuptools import setup
from synaps import version

class local_sdist(sdist.sdist):
    """Customized sdist hook - builds the ChangeLog file from VC first."""
    def run(self):
        common_setup.write_git_changelog()
        # sdist.sdist is an old style class, can't user super()
        sdist.sdist.run(self)

synaps_cmdclass = {'sdist': local_sdist}

def find_data_files(destdir, srcdir):
    package_data = []
    files = []
    for d in glob.glob('%s/*' % (srcdir,)):
        if os.path.isdir(d):
            package_data += find_data_files(
                                 os.path.join(destdir, os.path.basename(d)), d)
        else:
            files += [d]
    package_data += [(destdir, files)]
    return package_data

try: 
    from sphinx import setup_command

    class local_BuildDoc(setup_command.BuildDoc):
        def run(self):
            for builder in ['html', 'latex']:
                self.builder = builder
                self.finalize_options()
                setup_command.BuildDoc.run(self)
    synaps_cmdclass['build_sphinx'] = local_BuildDoc

except:
    pass

setup(
    name='synaps',
    version=version.canonical_version_string(),
    description='cloud monitoring system',
    author='Samsung SDS',
    author_email='june.yi@samsung.com',
    url='http://www.sdscloud.co.kr/',
    cmdclass=synaps_cmdclass,
    packages=find_packages(exclude=['bin']),
    include_package_data=True,
    scripts=['bin/synaps-syncdb',
             'bin/synaps-api-cloudwatch',
             'bin/synaps-reload-metric',
             'bin/synaps-meter',
             'bin/synaps-stress',
             ],
    setup_requires=[],
    py_modules=[]
)
