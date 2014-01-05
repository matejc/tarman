TarMan
======


This is archive manager with curses interface.
Have you ever wanted to create an archive quickly without
using help pages in the process for all the command line switches?
Well here comes the tarman, it has only two command line options:

    * --help or
    * path to archive or directory


At first it was meant to be only for tar archives (hence the name),
but support for other archives does not hurt. 
Dependencies are:

    * libarchive-dev
    * python-libarchive
    * Python 2.7 (or Python 2.6)


It supports archives that are manageable with libarchive.

For now it supports:

    * file browser
    * one-level browsing of supported archives
    * extraction of files
    * create archive option


Install from PYPI
=================

.. sourcecode:: bash

    pip install tarman


Usage
=====

.. sourcecode:: bash

    bin/tarman some/directory/


Key bindings
============

Key bindings are listed in HELP window,
you can access it by pressing *h* or *?* key.

{help_string}


Install of development version
==============================

It is very recommended to install it to virtualenv.

.. sourcecode:: bash

    git clone git://github.com/matejc/tarman.git 
    virtualenv --no-site-packages tarman
    cd tarman/
    bin/pip install .


Development
===========

.. sourcecode:: bash

    git clone git://github.com/matejc/tarman.git 
    virtualenv --no-site-packages tarman
    cd tarman/
    bin/python setup.py develop

