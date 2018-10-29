# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='src',
    version='0.0.0',
    description='Use alexa to create a smarthome',
    long_description='more description',
    author='Thomas Burke',
    author_email='tburke@bu.edu',
    url='https://github.com/thomasmburke/smarthome',
    packages=find_packages(exclude=('tests', 'docs'))
)
