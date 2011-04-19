#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distribute_setup import use_setuptools
use_setuptools()

import re
from setuptools import setup, find_packages
import os.path as p


def get_version():
    source = open(p.join(p.dirname(p.abspath(__file__)),
                         'src', 'jsonpipe', '__init__.py')).read()
    match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', source)
    if not match:
        raise RuntimeError("Couldn't find the version string in src/jsonpipe/__init__.py")
    return match.group(1)


setup(
    name='jsonpipe',
    version=get_version(),
    description="Convert JSON to a UNIX-friendly line-based format.",
    author='Zachary Voase',
    author_email='z@dvxhouse.com',
    url='http://github.com/dvxhouse/jsonpipe',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    entry_points={'console_scripts': ['jsonpipe = jsonpipe:main',
                                      'jsonunpipe = jsonpipe:main_unpipe']},
    install_requires=['simplejson>=2.1.3', 'argparse>=1.2.1', 'calabash>=0.0.2'],
    test_suite='jsonpipe._get_tests',
)
