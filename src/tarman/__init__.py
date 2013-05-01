from tarman.tree import DirectoryTree
from tarman.viewarea import ViewArea
from tarman.exceptions import OutOfRange
from tarman.containers import FileSystem
from tarman.containers import container
from tarman.containers import get_archive_class
from tarman.containers import Archive

import curses
import traceback
import argparse
import logging


class Main(object):

    def __init__(self, mainscr, stdscr, directory):
        logging.basicConfig(filename='tarman.log', filemode='w', level=logging.DEBUG)
        self.header_lns = 1
        self.mainscr = mainscr
        self.stdscr = stdscr
        self.color = curses.has_colors()
        if self.color:
            curses.init_pair(1, curses.COLOR_BLUE, -1)
            self.attr_folder = curses.color_pair(1) | curses.A_BOLD
            curses.init_pair(2, 7, -1)
            self.attr_norm = curses.color_pair(2)
        self.kill = False
        self.ch = -1
        self.visited = {}     # TODO
        self.area = None
        self.container = FileSystem()
        self.directory = self.container.abspath(directory)
        self.checked = DirectoryTree(self.directory, self.container)
        self.chdir(self.directory)

    def header(self, text, line=0):
        self.mainscr.clear()
        self.mainscr.addstr(line, 0, text)
        self.mainscr.refresh()

    def identify_container(self, path):
        if self.container.isenterable(path):  # is folder
            return self.container

        # force one-level archive browsing
        if not isinstance(self.container, FileSystem):
            return None

        return container(path)

    def chdir(self, newpath):
        if newpath is None:
            return False

        if not newpath.startswith(self.directory):
            return False

        try:
            if self.area is None:
                oldsel = 0
                oldpath = self.directory
            else:
                oldsel = self.area.selected
                oldpath = self.area.abspath

            oldcontainer = self.container
            oldchecked = self.checked

            if newpath in self.visited:
                newsel, newcontainer, newchecked = self.visited[newpath]
            else:
                newcontainer = self.identify_container(newpath)
                if newcontainer is None:
                    return False
                newchecked = DirectoryTree(newpath, newcontainer)
                newsel = 0

            self.visited[oldpath] = [oldsel, oldcontainer, oldchecked]
            logging.info("OLD - {0} - {1} - {2}".format(oldpath, oldsel, oldcontainer.__class__.__name__))
            logging.info("NEW - {0} - {1} - {2}".format(newpath, newsel, newcontainer.__class__.__name__))

            h, w = self.stdscr.getmaxyx()
            self.container = newcontainer
            self.checked = newchecked
            self.area = ViewArea(newpath, h, newcontainer)
            self.header("({0})  {1}".format(
                self.container.__class__.__name__, self.area.abspath
            ))
            self.area.set_params(h, offset=newsel)
            self.refresh_scr()

            return True
        except OutOfRange:
            curses.flash()

    def insert_line(self, y, item):
        i, name, abspath = item
        self.stdscr.addstr(
            y, 0, "[{0}]".format('*' if abspath in self.checked else ' ')
        )
        if self.color:
            if self.container.isenterable(abspath):
                attr = self.attr_folder
                name = "{0}/".format(name)
            else:
                attr = self.attr_norm

            self.stdscr.addstr(y, 5, name, attr)
        else:
            if self.container.isenterable(abspath):
                name = "{0}/".format(name)
            self.stdscr.addstr(y, 5, name)

    def refresh_scr(self):
        self.stdscr.clear()

        if len(self.area) == 0:
            self.stdscr.addstr(1, 5, "Directory is empty!")
            return

        iitem = 0
        for item in self.area:
            self.insert_line(iitem, item)
            iitem += 1

        y = self.area.selected_local

        h, w = self.stdscr.getmaxyx()
        self.stdscr.chgat(y, 0, w, curses.A_REVERSE)
        self.stdscr.move(y, 1)

    def loop(self):
        while not self.kill:
            self.ch = self.stdscr.getch()
            h, w = self.stdscr.getmaxyx()

            if self.ch in [ord('q'), 27]:
                self.kill = True

            elif self.ch == curses.KEY_UP:
                self.area.set_params(h, offset=-1)

            elif self.ch == curses.KEY_DOWN:
                self.area.set_params(h, offset=1)

            elif self.ch == curses.KEY_PPAGE:
                self.area.set_params(h, offset=-5)

            elif self.ch == curses.KEY_NPAGE:
                self.area.set_params(h, offset=5)

            elif self.ch == 32:
                index = self.area.selected
                if index == -1:
                    curses.flash()
                    continue
                abspath = self.area.get_abspath(index)
                if abspath in self.checked:
                    del self.checked[abspath]
                else:
                    self.checked.add(abspath, sub=True)

            elif self.ch == curses.KEY_RIGHT:
                index = self.area.selected
                if index == -1:
                    curses.flash()
                    continue
                abspath = self.area.get_abspath(index)
                if not self.chdir(abspath):
                    curses.flash()

            elif self.ch == curses.KEY_LEFT:
                if not self.chdir(
                    self.container.dirname(self.area.abspath)
                ):
                    curses.flash()

            elif self.ch in [ord('e'), ord('E')]:

                if isinstance(self.container, Archive):
                    aclass = self.container.__class__
                    archive = self.container.archive
                    checked = self.checked
                else:
                    index = self.area.selected
                    if index == -1:
                        curses.flash()
                        continue
                    abspath = self.area.get_abspath(index)
                    if not abspath:
                        curses.flash()
                        continue
                    aclass = get_archive_class(abspath)
                    archive = aclass.open(abspath)
                    checked = None
                aclass.extract(archive, '.', checked=checked)

            if self.ch != -1:
                self.refresh_scr()

            if self.kill:
                break

        self.stdscr.clear()

    def cancel(self):
        self.kill = True


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?", help="Directory.")
    args = parser.parse_args()

    try:
        # Initialize curses
        mainscr = curses.initscr()
        h, w = mainscr.getmaxyx()
        stdscr = curses.newwin(h - 1, w, 1, 0)

        curses.start_color()
        curses.use_default_colors()

        # Turn off echoing of keys, and enter cbreak mode,
        # where no buffering is performed on keyboard input
        curses.noecho()
        curses.cbreak()

        # In keypad mode, escape sequences for special keys
        # (like the cursor keys) will be interpreted and
        # a special value like curses.key_left will be returned
        stdscr.keypad(1)

        # getch will block for 500ms
        #stdscr.timeout(500)

        # getch will not block
        #stdscr.nodelay(1)

        main = Main(mainscr, stdscr, args.directory)
        main.loop()   # Enter the main loop

        # Set everything back to normal
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()                 # Terminate curses
    except:
        # In the event of an error, restore the terminal
        # to a sane state.
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        traceback.print_exc()           # Print the exception
        main.cancel()

    logging.info(main.visited)

    for item in main.checked:
        logging.info(item.get_path())


if __name__ == "__main__":
    main()
