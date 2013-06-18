# -*- coding: UTF-8 -*-

from tarman.containers import Container
from tarman.containers import FileSystem
from tarman.containers import LibArchive
from tarman.helpers import container
from tarman.tree import DirectoryTree

import libarchive
import os
import tarman.tests.test_containers
import tarman.tests.test_tree
import tempfile
import unittest2 as unittest


class TestFileSystem(unittest.TestCase):

    def setUp(self):
        self.fs = FileSystem()
        self.testcwd = os.getcwd()
        self.testfilepath = tarman.tests.test_containers.__file__
        self.testdirectory = os.path.dirname(self.testfilepath)

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
            self.fs.count_items(self.testdirectory),
            22
        )
        self.assertEqual(
            self.fs.count_items(self.testdirectory, stop_at=2),
            2
        )


class TestLibArchive(unittest.TestCase):

    def setUp(self):
        self.testfilepath = tarman.tests.test_containers.__file__
        self.testdirectory = os.path.dirname(self.testfilepath)
        self.testarchivepath = os.path.join(
            self.testdirectory, 'testdata', 'testdata.tar.gz'
        )
        self.testcontainer = LibArchive(self.testarchivepath)

    def test_listdir(self):
        self.assertEqual(
            self.testcontainer.listdir(self.testarchivepath),
            [u'a', u'b', u'c']
        )

    def test_isenterable(self):
        self.assertEqual(
            self.testcontainer.isenterable(self.testarchivepath),
            True
        )
        self.assertEqual(
            self.testcontainer.isenterable(
                os.path.join(self.testarchivepath, 'c')
            ),
            False
        )

    def test_abspath(self):
        self.assertEqual(
            self.testcontainer.abspath(
                os.path.join(self.testarchivepath, 'c')
            ),
            os.path.abspath(os.path.join(self.testarchivepath, 'c'))
        )

    def test_count_items(self):
        self.assertEqual(
            self.testcontainer.count_items(
                os.path.join(self.testarchivepath, 'a')
            ),
            3
        )
        self.assertEqual(
            self.testcontainer.count_items(
                os.path.join(self.testarchivepath, 'a'),
                stop_at=2
            ),
            2
        )

    def test_isarchive(self):
        self.assertTrue(
            LibArchive.isarchive(self.testarchivepath)
        )

    def test_open(self):
        with LibArchive.open(self.testarchivepath) as larchive:
            self.assertIsInstance(
                larchive,
                libarchive.Archive
            )

    def test_verify(self):
        self.assertFalse(
            LibArchive.verify(
                self.testarchivepath,
                '../abc',
                None
            )
        )
        self.assertFalse(
            LibArchive.verify(
                self.testarchivepath,
                '/abc',
                None
            )
        )
        self.assertTrue(
            LibArchive.verify(
                self.testarchivepath,
                'abc',
                None
            )
        )

    def test_verify_with_checked(self):
        checked = DirectoryTree(
            self.testarchivepath,
            self.testcontainer
        )
        checked.add(self.testcontainer.join(self.testarchivepath, 'a'), True)
        self.assertIn(
            self.testcontainer.join(self.testarchivepath, 'a', 'aa'),
            checked
        )

        self.assertFalse(
            LibArchive.verify(
                self.testarchivepath,
                'abc',
                checked
            )
        )

        self.assertTrue(
            LibArchive.verify(
                self.testarchivepath,
                'a/aa/aaa',
                checked
            )
        )

        self.assertTrue(
            LibArchive.verify(
                self.testarchivepath,
                'a/ab',
                checked
            )
        )

    def test_extract_all(self):

        tmpdir = tempfile.mkdtemp()

        LibArchive.extract(
            self.testcontainer,
            container(self.testarchivepath).archive,
            tmpdir
        )

        n = 0
        for prefix, files, dirs in os.walk(tmpdir):
            n += len(files) + len(dirs)

        self.assertEqual(n, 12)

        # clean up
        for root, dirs, files in os.walk(tmpdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(tmpdir)

    def test_extract_selective(self):

        path1 = self.testcontainer.join(self.testarchivepath, 'a/aa/aaa')
        path2 = self.testcontainer.join(self.testarchivepath, 'c')
        path3 = self.testcontainer.join(self.testarchivepath, 'a/ab')

        checked = DirectoryTree(
            self.testarchivepath,
            self.testcontainer
        )
        checked.add(path1, False)
        checked.add(path2, False)
        checked.add(path3, False)

        tmpdir = tempfile.mkdtemp()

        LibArchive.extract(
            self.testcontainer,
            container(self.testarchivepath).archive,
            tmpdir,
            checked
        )

        n = 0
        for prefix, files, dirs in os.walk(tmpdir):
            n += len(files) + len(dirs)

        self.assertEqual(n, 5)

        # clean up
        for root, dirs, files in os.walk(tmpdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(tmpdir)

    def test_create(self):
        testdatadirectory = os.path.join(
            self.testdirectory, 'testdata', 'testdata'
        )
        path1 = os.path.join(testdatadirectory, 'a', 'aa', 'aaa')
        path2 = os.path.join(testdatadirectory, 'c')
        path3 = os.path.join(testdatadirectory, 'a', 'ab')
        fs = FileSystem()

        checked = DirectoryTree(
            testdatadirectory,
            fs
        )
        checked.add(path1, False)
        checked.add(path2, False)
        checked.add(path3, False)

        tmpdir = tempfile.mkdtemp()

        testdata2archivepath = os.path.join(
            tmpdir, 'testdata2.tar.gz'
        )

        LibArchive.create(
            fs,
            testdata2archivepath,
            checked
        )

        self.assertTrue(os.path.exists(testdata2archivepath))

        testdata2archive = LibArchive(testdata2archivepath)
        apath1 = os.path.join(testdata2archivepath, 'a', 'aa', 'aaa')
        apath2 = os.path.join(testdata2archivepath, 'c')
        apath3 = os.path.join(testdata2archivepath, 'a', 'ab')
        self.assertIn(apath1, testdata2archive.tree)
        self.assertIn(apath2, testdata2archive.tree)
        self.assertIn(apath3, testdata2archive.tree)

        os.remove(testdata2archivepath)
        os.rmdir(tmpdir)

    def test_extract_utf8(self):

        tmpdir = tempfile.mkdtemp()

        testarchivepath = os.path.join(
            self.testdirectory, 'testdata', 'tešt.tar'
        )

        LibArchive.extract(
            self.testcontainer,
            container(testarchivepath).archive,
            tmpdir
        )

        n = 0
        for prefix, files, dirs in os.walk(tmpdir):
            n += len(files) + len(dirs)

        self.assertEqual(n, 1)
        self.assertTrue(os.path.exists(os.path.join(tmpdir, 'tarmanš.log')))

        # clean up
        for root, dirs, files in os.walk(tmpdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(tmpdir)

    def test_create_utf8(self):

        tmpdir = tempfile.mkdtemp()

        testarchivepath = os.path.join(
            self.testdirectory, 'testdata', 'tešt.tar'
        )

        LibArchive.extract(
            self.testcontainer,
            container(testarchivepath).archive,
            tmpdir
        )

        path1 = os.path.join(tmpdir, 'tarmanš.log')
        fs = FileSystem()

        checked = DirectoryTree(
            tmpdir,
            fs
        )
        checked.add(path1, False)

        testdata2archivepath = os.path.join(
            tmpdir, 'tešt2.tar'
        )

        LibArchive.create(
            fs,
            testdata2archivepath,
            checked
        )

        self.assertTrue(os.path.exists(testdata2archivepath))

        testdata2archive = LibArchive(testdata2archivepath)
        apath1 = os.path.join(testdata2archivepath, 'tarmanš.log')
        self.assertIn(apath1, testdata2archive.tree)

        # clean up
        for root, dirs, files in os.walk(tmpdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(tmpdir)
