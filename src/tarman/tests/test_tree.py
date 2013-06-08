
from tarman.containers import FileSystem
from tarman.exceptions import OutOfRange
from tarman.tree import DirectoryTree

import os
import tarman
import tempfile
import unittest2 as unittest


class TestDirectoryTree(unittest.TestCase):

    def setUp(self):
        self.testfilepath = tarman.tests.test_containers.__file__
        self.testdirectory = os.path.dirname(self.testfilepath)
        self.testdatapath = os.path.join(
            self.testdirectory, 'testdata', 'testdata'
        )
        self.fs = FileSystem()

    def test_init(self):
        self.assertIsNotNone(
            DirectoryTree(self.testdatapath, self.fs)
        )

    def test_add_file(self):
        tree = DirectoryTree(self.testdatapath, self.fs)
        path1 = self.fs.join(self.testdatapath, 'a', 'aa', 'aaa')
        path2 = self.fs.join(self.testdatapath, 'a', 'aa')
        tree.add(path1)
        self.assertIn(path1, tree)
        self.assertIn(path2, tree)  # not-added one-level-up directory

    def test_add_dir(self):
        tree = DirectoryTree(self.testdatapath, self.fs)
        dir1 = self.fs.join(self.testdatapath, 'a', 'ab')
        tree.add(dir1)
        self.assertIn(dir1, tree)

    def test_out_of_range(self):
        tree = DirectoryTree(self.testdatapath, self.fs)

        # one level up directory
        dir1 = self.fs.abspath(self.fs.join(self.testdatapath, '..'))
        with self.assertRaises(OutOfRange):
            tree.add(dir1)

        # completely different directory
        with tempfile.NamedTemporaryFile() as f:
            with self.assertRaises(OutOfRange):
                tree.add(f.name)
