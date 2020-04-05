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

    def utf8_return_function(self):
        return "sheeps"

    def test_utf8_return(self):
        self.assertIsInstance(self.utf8_return_function(), str)

    def utf8_args_by_index_function(self, text1=None, text2=None):
        return text1, text2

    def test_utf8_args_by_index(self):
        text1, text2 = self.utf8_args_by_index_function("sheeps1", "sheeps2")
        self.assertIsInstance(text1, str)
        self.assertIsInstance(text2, str)

    def utf8_args_by_keyword_function(self, text1=None, text2=None):
        return text1, text2

    def test_utf8_args_by_keyword(self):
        text1, text2 = self.utf8_args_by_keyword_function(
            "sheeps1", text2="sheeps2"
        )
        self.assertIsInstance(text1, str)
        self.assertIsInstance(text2, str)

    def utf8_args_combo_function(self, text1=None, text2=None):
        return text1, text2

    def test_utf8_args_combo(self):
        text1, text2 = self.utf8_args_by_keyword_function(
            "sheeps1", text2="sheeps2"
        )
        self.assertIsInstance(text1, str)
        self.assertIsInstance(text2, str)
