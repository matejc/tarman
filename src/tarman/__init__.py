from tarman.containers import Archive
from tarman.containers import container
from tarman.containers import FileSystem
from tarman.containers import get_archive_class
from tarman.exceptions import OutOfRange
from tarman.tree import DirectoryTree
from tarman.viewarea import ViewArea

import argparse
import curses
import curses.textpad
import logging
import os
import threading
import time
import traceback


class Main(object):

    def __init__(self, mainscr, stdscr, directory):
        logging.basicConfig(filename='tarman.log', filemode='w', level=logging.DEBUG)
        self.header_lns = 1
        self.mainscr = mainscr
        self.stdscr = stdscr
        self.overlaywin = Main.OverlayWin(self)
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

    class OverlayWin():

        def __init__(self, main):
            self.main = main
            self._clear_vars()

        def _clear_vars(self):
            self.showing = False
            self.newwin = None
            self.textwin = None
            self.textbox = None
            self.ch = None

        def show_text(self, text):
            self._clear_vars()
            lines, columns = self.main.stdscr.getmaxyx()
            height, width = 5, 10

            textdata = text.split('\n')
            height = len(textdata) + 4
            width = max([len(s) for s in textdata]) + 4

            self.showing = True
            self.exitstatus = -1
            self.newwin = self.main.stdscr.derwin(
                height, width, (lines / 2) - (height / 2), (columns / 2) - (width / 2)
            )

            self.newwin.border()
            self.newwin.touchwin()
            self.newwin.refresh()

            for i in range(len(textdata)):
                self.newwin.addstr(i + 2, 2, textdata[i])

            while self.showing:
                self.ch = self.newwin.getch()
                if self.ch in [27]:
                    self.close()

            self.main.mainscr.touchwin()
            self.main.mainscr.refresh()
            self.main.stdscr.touchwin()
            self.main.stdscr.refresh()
            self.main.refresh_scr()

        def show(self, text):
            """
            exitstatus:
                -2: path not exists
                -1: internal error
                 0: all ok
                 1: canceled
            """
            self._clear_vars()
            lines, columns = self.main.stdscr.getmaxyx()
            self.showing = True
            self.exitstatus = -1
            self.newwin = self.main.stdscr.derwin(
                5, columns, (lines / 2) - (5 / 2), 0
            )
            self.text = text
            self.newwin.border()
            self.newwin.addstr(1, 1, text)
            self.newwin.touchwin()
            self.newwin.refresh()

            self.textwin = self.newwin.derwin(
                2, columns - 2, 2, 1
            )
            self.textwin.touchwin()
            self.textwin.refresh()

            self.textbox = curses.textpad.Textbox(self.textwin, insert_mode=True)
            self.textbox.stripspaces = 1

            def run(handle):
                while handle.showing:
                    handle.refresh_exists()
                    time.sleep(0.2)

            t = threading.Thread(target=run, args=(self, ))
            t.setDaemon(True)
            t.start()

            s = self.textbox.edit(self.text_validator)
            self.showing = False

            self.main.mainscr.touchwin()
            self.main.mainscr.refresh()
            self.main.stdscr.touchwin()
            self.main.stdscr.refresh()
            self.main.refresh_scr()

            s = s.replace('\n', '').strip()
            if not os.path.exists(s):
                self.exitstatus = -2

            return self.exitstatus, s

        def text_validator(self, ch):
            y, x = self.textwin.getyx()
            maxy, maxx = self.textwin.getmaxyx()

            if ch in [27]:
                self.exitstatus = 1
                self.close()

            elif ch in [127, curses.ascii.BS, curses.KEY_BACKSPACE]:
                if x > 0:
                    self.textwin.move(y, x - 1)
                    self.textwin.delch()
                elif y == 0:
                    pass
                else:
                    self.textwin.move(y - 1, maxx - 1)
                    self.textwin.delch()

            elif ch in [330]:
                self.textwin.delch()

            elif ch in [10, 13]:
                self.exitstatus = 0
                self.close()

            elif ch in [curses.KEY_HOME]:
                self.textwin.move(0, 0)

            elif ch in [curses.KEY_END]:
                self.textwin.move(maxy - 1, maxx - 1)

            return ch

        def parse_gather_path(self):
            s = ''
            maxy, maxx = self.textwin.getmaxyx()
            cy, cx = self.textwin.getyx()

            for y in range(maxy):
                self.textwin.move(y, 0)
                for x in range(maxx):
                    s += chr(curses.ascii.ascii(self.textwin.inch(y, x)))

            self.textwin.move(cy, cx)
            return s.replace('\n', '').strip()

        def refresh_exists(self):
            path = self.parse_gather_path()

            exists = os.path.exists(path)

            s = "    Exists" if exists else "Not Exists"

            self.newwin.touchwin()
            self.newwin.refresh()

            if self.main.color:
                self.newwin.addstr(
                    1,
                    self.newwin.getmaxyx()[1] - len(s) - 1,
                    s,
                    self.main.attr_wright if exists else self.main.attr_wrong
                )
            else:
                self.newwin.addstr(
                    1,
                    self.newwin.getmaxyx()[1] - len(s) - 1,
                    s,
                )

            self.textwin.touchwin()
            self.textwin.refresh()

        def close(self):
            if self.textbox:
                self.textbox.do_command = lambda x: False
            self.showing = False

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
                exitstatus, s = self.overlaywin.show(
                    "Extract to "
                    "(press ENTER for confirmation or ESC to cancel):"
                )
                if exitstatus != 0:
                    continue

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
                    archive = aclass.open(abspath)
                    checked = None
                    container = None
                aclass.extract(container, archive, s, checked=checked)

                logging.info("Extracted to '{0}'".format(s))

            elif self.ch in [ord('?'), curses.KEY_F1, ord('h')]:
                self.overlaywin.show_text(
"""Browser window key bindings:
 h/?/F1  - this help window
 ESC/q   - quit
 up/down - move up or down in browser
 left    - go one directory up
 right   - go in to directory or archive
 e       - extract selected files
 space   - select and unselect files

Overlay window key bindings:
 ESC     - cancel/close
 ENTER   - confirm/ok"""
                )

            if self.ch != -1:
                self.refresh_scr()

            if self.kill:
                break

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

    logging.info(str(main.checked))
    for item in main.checked:
        logging.info(str(item.get_data_array()))


if __name__ == "__main__":
    main()
