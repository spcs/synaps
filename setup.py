import glob
import os

from setuptools import find_packages
from setuptools import setup
from synaps import version


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

setup(
    name='synaps',
    version=version.canonical_version_string(),
    description='monitoring system for SPCS',
    author='Samsung SDS',
    author_email='june.yi@samsung.com',
    url='http://www.sdscloud.co.kr/',
    packages=find_packages(exclude=['bin']),
    include_package_data=True,
    scripts=['bin/synaps-api-cloudwatch'],
    py_modules=[]
)
