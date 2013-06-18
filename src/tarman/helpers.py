
import tarman.containers

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


def s2u(s):
    """s2u - string to unicode, the safe way"""

    if isinstance(s, unicode):
        return s
    elif isinstance(s, str):
        return s.decode("utf8")
    else:
        try:
            return unicode(s)
        except:
            raise Exception("Ya talkin' gibberish? '{0}'".format(s))


class Utf8Args(object):

    def __init__(self, *argparams):
        self.param_ids = argparams

    def __call__(self, f, *argparams, **kwparams):
        for param_id in self.param_ids:
            try:
                int(param_id, 10)
                argparams[param_id] = s2u(argparams[param_id])
            except ValueError:  # it should be string
                kwparams[param_id] = s2u(kwparams[param_id])
        return f(*argparams, **kwparams)


def utf8_args(*param_ids):
    def wrap(f):
        def wrapped_f(*argparams, **kwparams):
            argparams = list(argparams)
            for param_id in param_ids:
                if isinstance(param_id, int):
                    argparams[param_id] = s2u(argparams[param_id])
                elif isinstance(param_id, str):
                    kwparams[param_id] = s2u(kwparams[param_id])
                else:
                    raise Exception(
                        "Wrong argument type: value:'{0}' type:{1}".format(
                            param_id, type(param_id)
                        )
                    )
            return f(*argparams, **kwparams)
        return wrapped_f
    return wrap


class Utf8Return(object):

    def __init__(self, f):
        self.f = f

    def __call__(self, *argparams, **kwparams):
        return s2u(self.f(*argparams, **kwparams))


def utf8_return(f):
    def wrap(*argparams, **kwparams):
        return s2u(f(*argparams, **kwparams))
    return wrap
