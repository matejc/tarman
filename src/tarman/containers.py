from tarman.exceptions import NotImplemented
from tarman.tree import DirectoryTree

import inspect
import os
import sys
import tarfile
import zipfile


def get_archive_class(path):
    classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    for c in classes:
        if c[0] == 'Archive':
            continue
        methods = inspect.getmembers(c[1], inspect.isfunction)
        for m in methods:
            if m[0] == 'isarchive':
                if m[1](path):
                    return c[1]
    return None


def container(path):
    aclass = get_archive_class(path)
    return aclass(path) if aclass else None


class Container():

    def listdir(self, path):
        raise NotImplemented()

    def isenterable(self, path):
        raise NotImplemented()

    def abspath(self, path):
        raise NotImplemented()

    def dirname(self, path):
        return os.path.dirname(path)

    def basename(self, path):
        return os.path.basename(path)

    def join(self, *parts):
        return os.path.join(*parts)

    def split(self, path):
        return os.path.split(path)

    def samefile(self, f1, f2):
        return f1.lower() == f2.lower()


class Archive():

    def __init__(self, path):
        raise NotImplemented()

    @staticmethod
    def isarchive(path):
        raise NotImplemented()

    @staticmethod
    def open(path):
        raise NotImplemented()

    @staticmethod
    def extract(archive, target_path, checked=None):
        raise NotImplemented()


class FileSystem(Container):

    def listdir(self, path):
        return os.listdir(path)

    def isenterable(self, path):
        return os.path.isdir(path)

    def abspath(self, path):
        return os.path.abspath(path)

    def dirname(self, path):
        return os.path.dirname(path)

    def basename(self, path):
        return os.path.basename(path)

    def join(self, *parts):
        return os.path.join(*parts)

    def split(self, path):
        return os.path.split(path)

    def samefile(self, f1, f2):
        return os.path.samefile(f1, f2)


class Dummy(Container):

    def listdir(self, path):
        if self.isenterable(path):
            return ['three1', 'three2', 'three3', 'three4', 'three5']
        return ['one', 'two', 'three', 'four', 'five']

    def isenterable(self, path):
        if path.endswith('three'):
            return True
        return False

    def abspath(self, path):
        return path

    def dirname(self, path):
        return os.path.dirname(path)

    def basename(self, path):
        return os.path.basename(path)

    def join(self, *parts):
        return os.path.join(*parts)

    def split(self, path):
        return os.path.split(path)

    def samefile(self, f1, f2):
        return f1 == f2
