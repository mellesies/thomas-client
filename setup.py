# -*- coding: utf-8 -*-

# Always prefer setuptools over distutils
from setuptools import setup, find_namespace_packages

# To use a consistent encoding
from codecs import open
import os
from os import path

here = path.abspath(path.dirname(__file__))
PKG_NAME = 'thomas-client'
PKG_DESC = "Client for Thomas' RESTful API and webinterface"

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    PKG_DESCRIPTION = f.read()


# Read the API version from disk. This file should be located in the package
# folder, since it's also used to set the pkg.__version__ variable.
version_path = os.path.join(here, 'thomas', 'client', '_version.py')
version_ns = {
    '__file__': version_path
}
with open(version_path) as f:
    exec(f.read(), {}, version_ns)


# Setup the package
setup(
    name=PKG_NAME,
    version=version_ns['__version__'],
    description=PKG_DESC,
    long_description=PKG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/mellesies/thomas-client',
    author='Melle Sieswerda',
    author_email='m.sieswerda@iknl.nl',
    packages=find_namespace_packages(include=['thomas.*']),
    package_data={
        "thomas.client": [
            "__build__",
        ],
    },
    python_requires='>= 3.6',
    install_requires=[
        'requests',
    ],)

