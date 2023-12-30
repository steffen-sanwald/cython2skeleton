#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='Cython2Skeleton',
    version='0.1.0',
    url='https://github.com/steffen-sanwald/cython2skeleton.git',
    author='Steffen Sanwald',
    author_email='author@gmail.com',
    description='Quickly gather highlevel insights into cython compiled executable/shared library.',
    packages=find_packages(),
    install_requires=['fire', 'binary2strings'],
)