from tarman.exceptions import NotImplemented
from tarman.tree import DirectoryTree

import inspect
import libarchive
import logging
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


def makepath(path):
    try:
        os.makedirs(path)
        return True
    except:
        return False


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
        if path[-1] == os.sep:
            path = path[:-1]
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
    def extract(container, archive, target_path, checked=None):
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

    def count_items(self, path, stop_at=-1):
        n = 0
        for rootdir, dirs, files in os.walk(path):
            for f in files:
                n += 1
            for d in dirs:
                n += 1
            if n >= stop_at:
                break
        return n


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


class Tar(Container, Archive):

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.archive = Tar.open(self.path)
        self.tree = DirectoryTree(self.path, self)
        names = self.archive.getnames()
        for n in names:
            self.tree.add(os.path.join(self.path, n))

    def listdir(self, path):
        children = self.tree[path].children
        return [c.data for c in children]

    def isenterable(self, path):
        arr = self.tree[path].get_data_array()[1:]
        return self.archive.getmember(os.sep.join(arr)).isdir()

    def abspath(self, path):
        return self.tree[path].get_path()

    @staticmethod
    def isarchive(path):
        return False  # disable
        return tarfile.is_tarfile(path)

    @staticmethod
    def open(path):
        return tarfile.open(path)

    @staticmethod
    def extract(container, archive, target_path, checked=None):
        if checked:
            members = []
            for node in checked:
                # without root data
                arr = container.tree[node.get_path()].get_data_array()[1:]
                if arr[0] == '..':
                    continue
                members += [archive.getmember(os.sep.join(arr))]
        else:
            members = None
        archive.extractall(path=target_path, members=members)


class Zip(Container, Archive):

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.archive = Zip.open(self.path)
        self.tree = DirectoryTree(self.path, self)
        names = self.archive.namelist()
        for n in names:
            if n[-1] == os.sep:
                continue
            self.tree.add(os.path.join(self.path, n))

    def listdir(self, path):
        children = self.tree[path].children
        return [c.data for c in children]

    def isenterable(self, path):
        children = self.tree[path].children
        return True if children else False

    def abspath(self, path):
        return self.tree[path].get_path()

    @staticmethod
    def isarchive(path):
        return False  # disable
        return zipfile.is_zipfile(path)

    @staticmethod
    def open(path):
        return zipfile.ZipFile(file=path)

    @staticmethod
    def extract(container, archive, target_path, checked=None):
        if checked:
            members = []
            for node in checked:
                # without root data
                arr = container.tree[node.get_path()].get_data_array()[1:]
                if arr[0] == '..':
                    continue
                members += [archive.getinfo(os.sep.join(arr))]
        else:
            members = None
        archive.extractall(path=target_path, members=members)


class LibArchive(Container, Archive):

    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.archive = LibArchive.open(self.path)
        self.tree = DirectoryTree(self.path, self)
        for entry in self.archive:
            pathname = entry.pathname
            if os.sep == pathname[0]:
                pathname = pathname[1:]
            self.tree.add(os.path.join(self.path, pathname))

    def listdir(self, path):
        children = self.tree[path].children
        return [c.data for c in children]

    def isenterable(self, path):
        children = self.tree[path].children
        return True if children else False

    def abspath(self, path):
        return self.tree[path].get_path()

    @staticmethod
    def isarchive(path):
        return libarchive.is_archive(path)

    @staticmethod
    def open(path):
        return libarchive.Archive(path)

    @staticmethod
    def extract(container, archive, target_path, checked=None):
        target_path = os.path.abspath(target_path)
        if checked:
            arch = libarchive.SeekableArchive(container.tree.root.get_path())
            for node in checked:
                # without root data
                arr = container.tree[node.get_path()].get_data_array()[1:]
                if arr[0] == '..':
                    continue
                pathname = os.sep.join(arr)
                path = os.path.join(target_path, pathname)
                logging.info("create: {0}".format(path))
                if node.is_dir():
                    makepath(path)
                else:
                    makepath(os.path.dirname(path))
                    arch.readpath(pathname, path)

        else:  # extract all
            for entry in archive:
                pathname = entry.pathname
                if pathname[0] == '/':
                    pathname = pathname[1:]
                path = os.path.join(target_path, pathname)
                logging.info("create: {0}".format(path))
                if entry.isdir():
                    makepath(path)
                else:
                    makepath(os.path.dirname(path))
                    archive.readpath(path)
