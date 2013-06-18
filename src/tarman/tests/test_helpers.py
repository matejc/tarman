from tarman.containers import LibArchive
from tarman.helpers import container
from tarman.helpers import get_archive_class
from tarman.helpers import utf8_return
from tarman.helpers import utf8_args

import os
import tarman.tests.test_containers
import unittest2 as unittest


class TestHelpers(unittest.TestCase):

    def setUp(self):
        self.testfilepath = tarman.tests.test_containers.__file__
        self.testdirectory = os.path.dirname(self.testfilepath)
        self.testarchivepath = os.path.join(
            self.testdirectory, 'testdata', 'testdata.tar.gz'
        )

    def test_get_archive_class(self):
        archive_class = get_archive_class(self.testarchivepath)
        self.assertEqual(archive_class, LibArchive)

    def test_container(self):
        c = container(self.testarchivepath)
        self.assertIsInstance(c, LibArchive)

    @utf8_return
    def utf8_return_function(self):
        return "sheeps"

    def test_utf8_return(self):
        self.assertIsInstance(self.utf8_return_function(), unicode)

    @utf8_args(2)
    def utf8_args_by_index_function(self, text1=None, text2=None):
        return text1, text2

    def test_utf8_args_by_index(self):
        text1, text2 = self.utf8_args_by_index_function("sheeps1", "sheeps2")
        self.assertIsInstance(text1, str)
        self.assertIsInstance(text2, unicode)

    @utf8_args('text2')
    def utf8_args_by_keyword_function(self, text1=None, text2=None):
        return text1, text2

    def test_utf8_args_by_keyword(self):
        text1, text2 = self.utf8_args_by_keyword_function(
            "sheeps1", text2="sheeps2"
        )
        self.assertIsInstance(text1, str)
        self.assertIsInstance(text2, unicode)

    @utf8_args(1, 'text2')
    def utf8_args_combo_function(self, text1=None, text2=None):
        return text1, text2

    def test_utf8_args_combo(self):
        text1, text2 = self.utf8_args_by_keyword_function(
            "sheeps1", text2="sheeps2"
        )
        self.assertIsInstance(text1, str)
        self.assertIsInstance(text2, unicode)
