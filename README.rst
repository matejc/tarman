TarMan
======

under construction


This is tar manager with curses interface.
It has no dependencies other than Python 2.7.
It supports archives that are manageable with modules tarfile and zipfile.

For now it supports:

    * curses browser of files
    * one-level browsing of supported archives
    * extraction of files to the current working directory
    * window for selecting extraction directory
    * help window


To be done:

    * compression of files and window for choosing archive options
    * password protection option of archives that support it


Installation to virtualenv
==========================

(very recommended, for now)

.. sourcecode:: bash

    git clone git://github.com/matejc/tarman.git 
    virtualenv --no-site-packages tarman
    cd tarman/
    bin/pip install .


Usage
=====

.. sourcecode:: bash

    bin/tarman some/directory/


Key bindings
============

Key bindings are listed in HELP window,
you can access it by pressing *h* or *?* key.


Development
===========

.. sourcecode:: bash

    git clone git://github.com/matejc/tarman.git 
    virtualenv --no-site-packages tarman
    cd tarman/
    bin/python setup.py develop
