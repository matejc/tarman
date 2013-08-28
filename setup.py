# -*- coding: utf-8 -*-
"""Installer for this package."""

from setuptools import setup
from setuptools import find_packages

import os
import sys


def import_path(fullpath):
    """
    Import a file with full path specification. Allows one to
    import from anywhere, something __import__ does not do.
    """
    path, filename = os.path.split(fullpath)
    filename, ext = os.path.splitext(filename)
    sys.path.append(path)
    module = __import__(filename)
    reload(module)  # Might be out of date
    del sys.path[-1]
    return module


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


constants = import_path(
    os.path.join(
        os.path.dirname(__file__), 'src', 'tarman', 'constants'
    )
)

long_description = \
    read('README.rst').format(help_string=constants.HELP_STRING) + \
    read('docs', 'HISTORY.rst') + \
    read('docs', 'LICENSE')

setup(
    name='tarman',
    version="0.1.3",
    description="",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Environment :: Console :: Curses",
        "Topic :: System :: Archiving",
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
    package_data={
        'tarman':
        [
            'tests/testdata/testdata/a/ac',
            'tests/testdata/testdata/a/ab/.git-keep',
            'tests/testdata/testdata/a/aa/aaa',
            'tests/testdata/testdata/c',
            'tests/testdata/testdata/b/ba/baa/baab',
            'tests/testdata/testdata/b/ba/baa/baaa/baaaa',
            'tests/testdata/testdata.tar.gz',
            'tests/testdata/tešt.tar',
            'tests/testdata/corrupted.tar',
        ]
    },
)
