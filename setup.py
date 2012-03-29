import glob
import os

from setuptools import find_packages
from setuptools import setup
from synaps import version

synaps_cmdclass = {}

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
    from sphinx.setup_command import BuildDoc

    class local_BuildDoc(BuildDoc):
        def run(self):
            for builder in ['html', 'man']:
                self.builder = builder
                self.finalize_options()
                BuildDoc.run(self)
    synaps_cmdclass['build_sphinx'] = local_BuildDoc

except:
    pass

setup(
    name='synaps',
    version=version.canonical_version_string(),
    description='monitoring system for SPCS',
    author='Samsung SDS',
    author_email='june.yi@samsung.com',
    url='http://www.sdscloud.co.kr/',
    cmdclass=synaps_cmdclass,
    packages=find_packages(exclude=['bin']),
    include_package_data=True,
    scripts=['bin/synaps-api-cloudwatch',
             'bin/synaps-db-initialsetup'],
    py_modules=[]
)
