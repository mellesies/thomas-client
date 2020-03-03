# -*- coding: utf-8 -*-

# Always prefer setuptools over distutils
from setuptools import setup, find_namespace_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
PKG_NAME = 'thomas-client'
PKG_DESC = "Client for Thomas' RESTful API and webinterface"

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    PKG_DESCRIPTION = f.read()


# Read the API version from disk
with open(path.join(here, 'thomas', 'client', 'VERSION')) as fp:
    PKG_VERSION = fp.read()


# Setup the package
setup(
    name=PKG_NAME,
    version=PKG_VERSION,
    description=PKG_DESC,
    long_description=PKG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/mellesies/thomas-client',
    author='Melle Sieswerda',
    author_email='m.sieswerda@iknl.nl',
    packages=find_namespace_packages(include=['thomas.*']),
    python_requires='>= 3.6',
    install_requires=[
        'requests',
    ],)

