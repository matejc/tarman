import sys
sys.path.append("/home/matej/Dropbox/matej/workarea/pys/tarman/src")

from tarman.tree import DirectoryTree


class ViewArea():
    """List of files and directories for area on screen.
    When you change directory, create new instance.
    """

    def __init__(self, path, height, container):
        self.abspath = path
        self.container = container
        self.list = sorted(self.container.listdir(self.abspath))
        self.first = self.selected = 0
        self.last = -1
        self.set_params(height)

    def set_params(self, height, offset=0):
        self.height = height
        list_len = len(self.list)
        sel_old = self.selected
        sel_new = sel_old + offset

        if sel_new < 0:
            sel_new = 0
        elif sel_new >= list_len:
            sel_new = list_len - 1

        if list_len <= self.height:
            self.first = 0
            self.last = list_len - 1
            self.selected = sel_new
        else:
            first_old = self.first
            last_old = self.first + self.height - 1

            if sel_new > last_old:
                self.last = sel_new
                self.first += self.last - last_old
            elif sel_new < first_old:
                self.first = sel_new
                self.last -= first_old - self.first
            else:
                self.first = first_old
                self.last = last_old

            self.selected = sel_new

        self.selected_local = self.selected - self.first

    def get_abspath(self, index):
        try:
            return self.container.join(self.abspath, self[index])
        except IndexError:
            return None

    def get_selected_abs(self):
        return self.get_abspath(self.selected)

    def get_selected_name(self):
        return self[self.selected]

    def __getitem__(self, key):
        return self.list[key]

    def __iter__(self):
        for i in range(self.first, self.last + 1):
            name = self.list[i]
            abspath = self.container.join(self.abspath, name)
            yield (
                i,
                name,
                abspath
            )

    def __len__(self):
        return self.last - self.first + 1


def print_area(path):
    area = ViewArea(path, 4)
    off = 8
    area.set_params(4, offset=off)
    print "{0} of {1}, offset:{2}, path: '{3}'".format(len(area), len(area.list), off, area.abspath)
    for item in area:
        print item


if __name__ == "__main__":

    tree = DirectoryTree("/home/matej/workarea/matejc.myportal/src")

    a1 = tree.add("a1")
    a2 = tree.add("/home/matej/workarea/matejc.myportal/"
        "src/matejc/myportal/profiles", True)
    a3 = tree.add(
        "/home/matej/workarea/matejc.myportal/src/matejc/__init__.py"
    )

    print_area("/home/matej/workarea/matejc.myportal/src/")
    print_area("/home/matej/workarea/matejc.myportal/src/matejc/myportal")
