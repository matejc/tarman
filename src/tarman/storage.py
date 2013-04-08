import sys
sys.path.append("/home/matej/Dropbox/matej/workarea/pys/tarman/src")

from tarman.exceptions import NotFound

import os


class Checked():
    """This is storage for checked
    files or directories for whole application.
    """

    def __init__(self, rootdir):
        self.rootdir = rootdir
        self.data = {}

    def _add_file(self, abspath):
        abspath, relpath = self._abs_rel_path(abspath)
        path, name = os.path.split(relpath)

        if path in self.data:
            self.data[path].add(name)
        else:
            self.data[path] = set([name])

    def _add_to_data(self, abspath):
        abspath, relpath = self._abs_rel_path(abspath)

        if not os.path.isdir(abspath):
            self._add_file(abspath)
            return

        lst = os.listdir(abspath)
        if len(lst) == 0:
            self.data[relpath] = set([])

        for name in lst:
            apath = os.path.join(abspath, name)
            if os.path.isdir(apath):
                self._add_to_data(apath)
            else:
                self._add_file(apath)

    def _abs_rel_path(self, path):
        if os.path.isabs(path):
            abspath = path
            relpath = abspath[len(self.rootdir) + 1:]
        else:
            relpath = path
            abspath = os.path.join(self.rootdir, relpath)
        return abspath, relpath

    def __add__(self, path):
        if os.path.isabs(path):
            abspath = path
            relpath = abspath[len(self.rootdir):]
        else:
            relpath = path
            abspath = os.path.join(self.rootdir, relpath)

        if not os.path.exists(abspath):
            raise NotFound(abspath)

        self._add_to_data(abspath)
        return self

    def __contains__(self, key):
        abspath, relpath = self._abs_rel_path(key)

        try:
            if relpath in self.data:
                return True

            a, b = os.path.split(relpath)
            if b in self.data[a]:
                return True

            return False
        except KeyError:
            return False

    def __delitem__(self, key):
        abspath, relpath = self._abs_rel_path(key)

        if relpath in self.data:
            del self.data[relpath]
            return

        a, b = os.path.split(relpath)
        if b in self.data[a]:
            self.data[a].remove(b)

    def __iter__(self):
        for directory in self.data:
            if self.data[directory]:
                for name in self.data[directory]:
                    yield os.path.join(self.rootdir, directory, name)
            else:
                yield os.path.join(self.rootdir, directory)


class ViewArea():
    """List of files and directories for area on screen.
    When you change directory, create new instance.
    """

    def __init__(self, path, checked):
        self.checked = checked
        self.abspath, self.relpath = checked._abs_rel_path(path)
        self.list = sorted(os.listdir(self.abspath))
        self.first = self.selected = 0
        self.last = self.height = self.width = -1

    def _move_area(self, offset=0):
        list_len = len(self.list)

        first = self.first + offset
        if first >= list_len:
            self.first = max(list_len - self.height, 0)
        elif first < 0:
            self.first = 0
        else:
            self.first = first

        last = self.height + self.first
        if last >= list_len:
            self.first = max(list_len - self.height, 0)
            self.last = list_len
            print self.first
        else:
            self.last = last

    def _move_index(self, offset=0):
        self._move_area(offset=0)

        y = self.selected + offset

        if y < self.first:
            self._move_area(offset=offset)
            y = self.first

        if y >= self.last:
            self._move_area(offset=offset)
            y = self.last - 1

        self.selected = y
        self.selected_local = y - self.first

    def set_params(self, width, height, offset=0):
        self.width = width
        self.height = height
        self._move_index(offset=offset)

    def get_abspath(self, index):
        return os.path.join(self.abspath, self[index])

    def get_selected_abs(self):
        return self.get_abspath(self.selected)

    def get_selected_name(self):
        return self[self.selected]

    def __getitem__(self, key):
        return self.list[key]

    def __iter__(self):
        print self.first, self.last
        for i in range(self.first, self.last):
            name = self.list[i]
            abspath = os.path.join(self.abspath, name)
            yield (
                i,
                name,
                abspath,
                abspath in self.checked
            )


if __name__ == "__main__":

    checked = Checked(
        "/home/matej/Dropbox/matej/workarea/pys/tarman"
    )

    area = ViewArea("", checked)
    area.set_params(50, 5, offset=8)
    print area.abspath
    for item in area:
        print item

    """
    st += "matejc/myportal/profiles/default"
    st += "/home/matej/workarea/matejc.myportal/src/matejc/myportal"

    del st["matejc/myportal/testing"]
    del st["matejc/myportal/profiles/default/metadata.xml"]
    del st["matejc/myportal/profiles/default/browserlayer.xml"]
    del st["matejc/myportal/profiles/default/matejc.myportal.marker.txt"]

    print st.rootdir
    from pprint import pprint
    pprint(st.data)

    print "matejc/myportal/profiles/default" in st

    for a in st:
        print a
"""
