#!/usr/bin/env python
# -*- coding: utf-8 -*-
""""setup.py

Note: Do a Python check

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
from __future__ import print_function

from io import open
import os
from os import path
import sys

from setuptools import setup


v = sys.version_info

if v[:2] < (3, 6):
    print('ERROR: Bookstore requires Python 3.6 or higher', file=sys.stderr)
    sys.exit(1)

# We have the correct Python version, proceed.

pjoin = os.path.join

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(pjoin(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Get the bookstore version
ns = {}
with open(pjoin(here, 'bookstore', '_version.py')) as f:
    exec(f.read(), {}, ns)


target_dir = pjoin("etc", "jupyter", "jupyter_notebook_config.d")
config_files = [pjoin("jupyter_config", "jupyter_notebook_config.d", "bookstore.json")]
data_files = [(target_dir, config_files)]

setup(
    name='bookstore',
    version=ns['__version__'],
    description='Storage Workflows for Notebooks',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nteract/bookstore',
    author='nteract contributors',
    author_email='nteract@googlegroups.com',
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    # Note that this is a string of words separated by whitespace, not a list.
    keywords='jupyter storage nteract notebook',
    packages=['bookstore'],
    install_requires=[
        'future',
        'futures ; python_version < "3.0"',
        'ipython >= 5.0',
        'notebook',
        's3fs',
        'tornado >= 5.1.1',
        'aiobotocore>=0.10.0',
        'aioboto3',
    ],
    extras_require={
        'test': [
            'codecov',
            'coverage',
            'mock',
            'mypy==0.660',
            'pytest>=3.3',
            'pytest-cov',
            'pytest-mock',
            'black',
        ]
    },
    data_files=data_files,
    entry_points={},
    project_urls={
        'Documentation': 'https://github.com/nteract/bookstore/#todo',
        'Funding': 'https://nteract.io',
        'Source': 'https://github.com/nteract/bookstore/',
        'Tracker': 'https://github.com/nteract/bookstore/issues',
    },
)
