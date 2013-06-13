from libarchive import _libarchive
from tarman.exceptions import NotImplemented
from tarman.exceptions import OutOfRange
from tarman.tree import DirectoryTree

import inspect
import libarchive
import logging
import os
import stat
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
        logging.info("makepath '{0}'".format(path))
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
                if n == stop_at:
                    return n
            for d in dirs:
                n += 1
                if n == stop_at:
                    return n
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
        self.tree = DirectoryTree(self.path, self)
        with LibArchive.open(self.path) as larchive:
            self.archive = larchive
            for entry in larchive:
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

    def count_items(self, path, stop_at=-1):
        node = self.tree[path]
        n = 0
        for p in node.__iter__():
            n += 1
            if n == stop_at:
                break
        return n

    @staticmethod
    def isarchive(path):
        try:
            return libarchive.is_archive(path)
        except:
            return libarchive.is_archive_name(path)

    @staticmethod
    def open(path):
        return libarchive.Archive(path)

    @staticmethod
    def verify(archive_path, pathname, checked):
        # do not allow to go up in the directory tree like that
        if pathname.startswith('..'):
            return False

        # do not allow absolute paths
        if pathname[0] == '/':
            return False

        # if none is checked, that means, extract all
        if not checked:
            return True

        # if file is checked, extract it
        try:
            if "/".join([archive_path, pathname]) in checked:
                return True
        except OutOfRange:  # this is expected
            return False

        # return false if file is not checked
        return False

    @staticmethod
    def extract(container, archive, target_path, checked=None):
        target_path = os.path.abspath(target_path)
        archive_path = archive.filename

        # reopen archive file
        archive.denit()
        archive.f.seek(0)
        archive.init()

        a = archive._a
        try:
            if checked:
                logging.info("START extract selective '{0}'".format(
                    archive_path
                ))
                while True:
                    try:
                        e = _libarchive.archive_entry_new()
                        r = _libarchive.archive_read_next_header2(a, e)
                        if r != _libarchive.ARCHIVE_OK:
                            break

                        pathname = _libarchive.archive_entry_pathname(e)
                        if pathname[-1] == '/':
                            pathname = pathname[:-1]

                        path = os.path.join(target_path, pathname)

                        logging.info("from '{0}' to '{1}'".format(
                            pathname, path
                        ))

                        if LibArchive.verify(archive_path, pathname, checked):
                            ftype = _libarchive.archive_entry_filetype(e)
                            if stat.S_ISDIR(ftype):
                                makepath(path)
                            else:
                                makepath(os.path.dirname(path))
                                with open(path, 'wb') as f:
                                    _libarchive.archive_read_data_into_fd(
                                        a, f.fileno()
                                    )
                    finally:
                        _libarchive.archive_entry_free(e)

                logging.info("END extract selective '{0}'".format(
                    archive_path
                ))

            else:
                logging.info("START extract all '{0}'".format(archive_path))
                while True:
                    try:
                        e = _libarchive.archive_entry_new()
                        r = _libarchive.archive_read_next_header2(a, e)
                        if r != _libarchive.ARCHIVE_OK:
                            break
                        pathname = _libarchive.archive_entry_pathname(e)
                        path = os.path.join(target_path, pathname)

                        logging.info("from '{0}' to '{1}'".format(
                            pathname, path
                        ))

                        if stat.S_ISDIR(_libarchive.archive_entry_filetype(e)):
                            makepath(path)
                        else:
                            makepath(os.path.dirname(path))
                            with open(path, 'wb') as f:
                                _libarchive.archive_read_data_into_fd(
                                    a, f.fileno()
                                )
                    finally:
                        _libarchive.archive_entry_free(e)
                logging.info("END extract all '{0}'".format(archive_path))
        finally:
            archive.close()

    @staticmethod
    def create(container, archivepath, checked):
        if not isinstance(container, FileSystem):
            logging.info("container '{0}' is not FileSystem".format(container))
            return False

        archivepath = os.path.abspath(archivepath)

        try:
            with libarchive.Archive(archivepath, 'w') as a:
                logging.info("START create selective '{0}'".format(
                    archivepath
                ))
                for node in checked:
                    path = node.get_path()
                    pathname = os.path.join(*node.get_data_array()[1:])
                    logging.info("from '{0}' to '{1}'".format(
                        path, pathname
                    ))
                    a.writepath(path, pathname)
                logging.info("END create selective '{0}'".format(archivepath))
        except Exception as e:
            logging.info("Exception '{0}': {1}".format(e))
            return False
        return True

        """
        a = _libarchive.archive_write_new()
        _libarchive.archive_write_add_filter_gzip(a)
        _libarchive.archive_write_set_format_pax_restricted(a)
        _libarchive.archive_write_open_filename(a, archivepath, 10240)

        # TODO from here:

        while True:
            e = _libarchive.archive_entry_new()
            try:
                r = _libarchive.archive_read_next_header2(a, e)
                if r != _libarchive.ARCHIVE_OK:
                    break
                n = _libarchive.archive_entry_pathname(e)
                if n != 'my_file.txt':
                    continue
                l = _libarchive.archive_entry_size(e)
                s = _libarchive.archive_read_data_into_str(a, l)
                print 'File Contents:', s
            finally:
                _libarchive.archive_entry_free(e)
        _libarchive.archive_read_close(a)
        _libarchive.archive_read_free(a)
        """
