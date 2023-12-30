#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'cython2skeleton'
DESCRIPTION = 'Quickly gather highlevel insights into cython compiled executable/shared library.'
URL = 'https://github.com/steffen-sanwald/cython2skeleton'
AUTHOR = 'Steffen Sanwald'
REQUIRES_PYTHON = '>=3.11.0'
VERSION = '0.1.0'

# What packages are required for this module to be executed?
REQUIRED = [
    'fire',
    'binary2strings'
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}
