import sys
sys.path.append("/home/matej/Dropbox/matej/workarea/pys/tarman/src")

from tarman.exceptions import NotImplemented

import os


class Container():

    def listdir(self, path):
        raise NotImplemented()

    def isdir(self, path):
        raise NotImplemented()

    def abspath(self, path):
        raise NotImplemented()

    def dirname(self, path):
        raise NotImplemented()

    def basename(self, path):
        raise NotImplemented()

    def join(self, *parts):
        raise NotImplemented()

    def split(self, path):
        raise NotImplemented()

    def samefile(self, f1, f2):
        raise NotImplemented()


class FileSystem(Container):

    def listdir(self, path):
        return os.listdir(path)

    def isdir(self, path):
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
