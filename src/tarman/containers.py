import os
import tarfile
import zipfile

from tarman.exceptions import NotImplemented
from tarman.tree import DirectoryTree


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

    def count_items(self, path, stop_at=-1):
        count = 0
        if self.isenterable(path):
            for name in self.listdir(path):
                count += self.count_items(self.join(path, name), stop_at)
        else:
            count += 1
        return count


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
        try:
            return os.listdir(path)
        except OSError:
            return []

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

        for _, dirs, files in os.walk(path):
            for f in files:
                n += 1
                if n == stop_at:
                    return n
            for d in dirs:
                n += 1
                if n == stop_at:
                    return n
        return n


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

