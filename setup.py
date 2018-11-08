# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='src',
    version='0.0.0',
    description='Use alexa to create a smarthome',
    long_description=readme(),
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English'
        ],
    author='Thomas Burke',
    author_email='tburke@bu.edu',
    url='https://github.com/thomasmburke/smarthome',
    packages=find_packages(exclude=('tests', 'docs'))
)
