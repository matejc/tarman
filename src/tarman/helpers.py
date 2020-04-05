
import tarman.containers

import codecs
import inspect
import sys
import os


def get_archive_class(path):
    classes = inspect.getmembers(
        sys.modules[tarman.containers.__name__], inspect.isclass
    )

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

