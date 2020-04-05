# -*- coding: UTF-8 -*-

from tarman.containers import Container
from tarman.containers import FileSystem

import os
import tarman.tests.test_containers
import tarman.tests.test_tree
import unittest2 as unittest


class TestFileSystem(unittest.TestCase):

    def setUp(self):
        self.fs = FileSystem()
        self.testcwd = os.getcwd()
        self.testfilepath = tarman.tests.test_containers.__file__
        self.testdirectory = os.path.dirname(self.testfilepath)
        self.testdatadir = os.path.join(self.testdirectory, 'testdata')

    def test_container(self):
        self.assertTrue(isinstance(self.fs, Container))

    def test_listdir(self):
        self.assertEqual(
            self.fs.listdir(self.testdirectory),
            os.listdir(self.testdirectory)
        )

    def test_isenterable(self):
        self.assertTrue(self.fs.isenterable(self.testdirectory))

    def test_abspath(self):
        self.assertEqual(self.fs.abspath('.'), self.testcwd)

    def test_dirname(self):
        self.assertEqual(
            self.fs.dirname(self.testfilepath), self.testdirectory
        )

    def test_basename(self):
        self.assertEqual(
            self.fs.basename(self.testfilepath),
            os.path.basename(self.testfilepath)
        )

    def test_join(self):
        self.assertEqual(
            self.fs.join('/home', 'someone', 'bin', 'python'),
            '/home/someone/bin/python'
        )

    def test_split(self):
        self.assertEqual(
            self.fs.split('/home/someone/bin/python'),
            ('/home/someone/bin', 'python')
        )

    def test_samefile(self):
        self.assertTrue(
            self.fs.samefile(self.testfilepath, self.testfilepath)
        )
        self.assertFalse(
            self.fs.samefile(
                self.testfilepath,
                tarman.tests.test_tree.__file__
            )
        )

    def test_count_items(self):
        self.assertEqual(
            self.fs.count_items(self.testdatadir),
            17
        )
        self.assertEqual(
            self.fs.count_items(self.testdatadir, stop_at=9),
            9
        )
