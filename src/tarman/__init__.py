from tarman.containers import Archive
from tarman.containers import container
from tarman.containers import FileSystem
from tarman.containers import get_archive_class
from tarman.exceptions import OutOfRange
from tarman.tree import DirectoryTree
from tarman.viewarea import ViewArea
from tarman.overlaywin import TextWin
from tarman.overlaywin import WorkWin
from tarman.overlaywin import PathWin
from tarman.overlaywin import QuestionWin

import argparse
import curses
import curses.textpad
import logging
import os
import traceback

HEADER_LNS = 1
ITEMS_WARNING = 10000


class Main(object):

    def __init__(self, mainscr, stdscr, directory):
        logging.basicConfig(
            filename='tarman.log', filemode='w', level=logging.DEBUG
        )
        self.header_lns = HEADER_LNS
        self.mainscr = mainscr
        self.stdscr = stdscr
        self.color = curses.has_colors()
        if self.color:
            # set file type attributes (color and bold)
            curses.init_pair(1, curses.COLOR_BLUE, -1)
            self.attr_folder = curses.color_pair(1) | curses.A_BOLD
            curses.init_pair(2, 7, -1)
            self.attr_norm = curses.color_pair(2)

            # set wright / wrong attributes (color and bold)
            curses.init_pair(3, curses.COLOR_GREEN, -1)
            self.attr_wright = curses.color_pair(3) | curses.A_BOLD

            curses.init_pair(4, curses.COLOR_RED, -1)
            self.attr_wrong = curses.color_pair(4) | curses.A_BOLD

        self.kill = False
        self.ch = -1
        self.visited = {}
        self.area = None
        self.container = FileSystem()
        self.directory = self.container.abspath(directory)
        self.checked = DirectoryTree(self.directory, self.container)
        self.chdir(self.directory)

    def header(self, text):
        #self.mainscr.clear()
        h, w = self.mainscr.getmaxyx()
        length = len(text)
        empty = 0
        if length > w:
            text = "..." + text[length - w + 3:]
        else:
            empty = w - length
        self.mainscr.addstr(0, 0, text + (empty * ' '))
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
                workwin = WorkWin(self)
                workwin.show("Working ...")

                newcontainer = self.identify_container(newpath)

                workwin.close()

                if newcontainer is None:
                    return False
                newchecked = DirectoryTree(newpath, newcontainer)
                newsel = 0

            self.visited[oldpath] = [oldsel, oldcontainer, oldchecked]
            logging.info("OLD - {0} - {1} - {2}".format(
                oldpath, oldsel, oldcontainer.__class__.__name__
            ))
            logging.info("NEW - {0} - {1} - {2}".format(
                newpath, newsel, newcontainer.__class__.__name__
            ))

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
            logging.error("OutOfRange .. {0}".format(newpath))
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

            if self.ch in [ord('q'), ]:
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
                    if isinstance(self.container, FileSystem) and \
                        self.container.count_items(
                            abspath, stop_at=ITEMS_WARNING
                        ) >= ITEMS_WARNING and \
                            self.show_items_warning() != 0:
                                continue
                    self.checked.add(abspath, sub=True)

            elif self.ch in [curses.KEY_RIGHT, 10, 13]:
                index = self.area.selected
                if index == -1:
                    curses.flash()
                    continue
                abspath = self.area.get_abspath(index)

                result = self.chdir(abspath)
                if not result:
                    curses.flash()

            elif self.ch in [curses.KEY_LEFT,
                             127, curses.ascii.BS, curses.KEY_BACKSPACE]:
                if not self.chdir(
                    self.container.dirname(self.area.abspath)
                ):
                    curses.flash()

            elif self.ch in [ord('e'), ord('E')]:
                if isinstance(self.container, Archive):
                    aclass = self.container.__class__
                    archive = self.container.archive
                    checked = self.checked
                    container = self.container
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
                    if aclass is None:
                        curses.flash()
                        continue
                    archive = aclass.open(abspath)
                    checked = None
                    container = None

                pathwin = PathWin(self)
                exitstatus, s = pathwin.show(
                    "Extract to "
                    "(press ENTER for confirmation or ESC to cancel):"
                )
                pathwin.close()
                if exitstatus != 0:
                    continue

                workwin = WorkWin(self)
                workwin.show("Extracting ...")
                aclass.extract(container, archive, s, checked=checked)
                workwin.close()

                TextWin(self).show("Extracted to:\n{0}".format(s))

                logging.info("extracted to '{0}'".format(s))

            elif self.ch in [ord('?'), curses.KEY_F1, ord('h')]:
                textwin = TextWin(self)
                textwin.show("""Browser window key bindings:
 h/?/F1         - this help window
 q              - quit
 UP/DOWN        - move up or down in browser
 LEFT/BACKSPACE - go one directory up
 RIGHT/ENTER    - go in to directory or archive
 e              - extract selected files
 SPACE          - select and unselect files

Overlay window key bindings:
 ESC            - cancel/close
 ENTER          - confirm/ok""")

            if self.ch != -1:
                self.refresh_scr()

            if self.kill:
                break

    def show_items_warning(self):
        questionwin = QuestionWin(self)
        return questionwin.show(
            "There are more than {0} items in this folder,"
            "\ndo you really want to select it?".format(
                ITEMS_WARNING
            )
        )

    def cancel(self):
        self.kill = True


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?", help="Directory.", default='.')
    args = parser.parse_args()

    # we need faster esc delay for more responsive program
    os.environ['ESCDELAY'] = '25'

    try:

        # Initialize curses
        mainscr = curses.initscr()
        h, w = mainscr.getmaxyx()
        stdscr = curses.newwin(h - HEADER_LNS, w, HEADER_LNS, 0)

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

    logging.info(str(main.checked))
    for item in main.checked:
        logging.info(str(item.get_data_array()))


if __name__ == "__main__":
    main()
