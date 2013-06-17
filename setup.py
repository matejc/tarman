# -*- coding: utf-8 -*-
"""Installer for this package."""

from setuptools import setup
from setuptools import find_packages

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = \
    read('README.rst') + \
    read('docs', 'HISTORY.rst') + \
    read('docs', 'LICENSE')

setup(
    name='tarman',
    version="0.1",
    description="",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
    ],
    keywords='tar zip archive curses',
    author='Matej Cotman',
    author_email='cotman.matej@gmail.com',
    url='https://github.com/matejc/tarman',
    license='BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    zip_safe=False,
    install_requires=[
        'setuptools',
        'python-libarchive',
    ],
    tests_require=[
        'mock',
        'nose',
        'unittest2'
    ],
    entry_points={
        'console_scripts': [
            "tarman = tarman:main",
        ]
    },
    test_suite='nose.collector',
)
