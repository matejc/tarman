import sys
sys.path.append("/home/matej/Dropbox/matej/workarea/pys/tarman/src")

from tarman.storage import Checked
from tarman.storage import ViewArea

import curses
import traceback
import os
import argparse
import stat


class Main(object):

    def __init__(self, mainscr, stdscr, directory):
        self.header_lns = 1
        self.mainscr = mainscr
        self.stdscr = stdscr
        self.color = curses.has_colors()    # TODO
        if self.color:
            curses.init_pair(1, curses.COLOR_BLUE, -1)
            self.attr_folder = curses.color_pair(1) | curses.A_BOLD
            curses.init_pair(2, 7, -1)
            self.attr_hidden = curses.color_pair(2)
            self.attr_norm = curses.A_NORMAL
            curses.init_pair(3, curses.COLOR_CYAN, -1)
            self.attr_link = curses.color_pair(3) | curses.A_BOLD
            curses.init_pair(4, curses.COLOR_GREEN, -1)
            self.attr_exec = curses.color_pair(4) | curses.A_BOLD
        self.kill = False
        self.ch = -1
        self.directory = os.path.abspath(directory)
        self.checked = Checked(self.directory)
        self.visited = {}     # TODO
        self.chdir(self.directory)

    def header(self, text, line=0):
        self.mainscr.clear()
        self.mainscr.addstr(line, 0, text)
        self.mainscr.refresh()

    def chdir(self, path):
        self.area = ViewArea(path, self.checked)
        self.header(self.area.abspath)
        h, w = self.stdscr.getmaxyx()
        self.area.set_params(w, h)
        self.refresh_scr()

    def insert_line(self, y, item):
        i, name, abspath, check = item
        self.stdscr.addstr(
            y, 0, "[{0}]".format('*' if check else ' ')
        )
        statinfo = os.stat(abspath)
        mode = statinfo.st_mode
        if self.color:

            if stat.S_ISREG(mode):
                if (stat.S_IXUSR & mode) or \
                        (stat.S_IXGRP & mode) or \
                            (stat.S_IXOTH & mode):
                    attr = self.attr_exec
                else:
                    attr = self.attr_norm

            elif stat.S_ISDIR(mode):
                attr = self.attr_folder
                name = "{0}/".format(name)

            elif stat.S_IFLNK & mode:  # not working, don't know why
                attr = self.attr_link

            self.stdscr.addstr(y, 5, name, attr)
        else:
            self.stdscr.addstr(y, 5, name)

    def refresh_scr(self):
        self.stdscr.clear()

        iitem = 0
        for item in self.area:
            self.insert_line(iitem, item)
            iitem += 1

        y = self.area.selected_local

        self.stdscr.chgat(y, 0, self.area.width, curses.A_REVERSE)
        self.stdscr.move(y, 1)

    def loop(self):
        while not self.kill:
            self.ch = self.stdscr.getch()
            h, w = self.stdscr.getmaxyx()

            if self.ch in [ord('q'), 27]:
                self.kill = True

            elif self.ch == curses.KEY_UP:
                self.area.set_params(w, h, offset=-1)

            elif self.ch == curses.KEY_DOWN:
                self.area.set_params(w, h, offset=1)

            elif self.ch == curses.KEY_PPAGE:
                self.area.set_params(w, h, offset=-5)

            elif self.ch == curses.KEY_NPAGE:
                self.area.set_params(w, h, offset=5)

            elif self.ch == 32:
                pass

            elif self.ch == curses.KEY_RIGHT:
                abspath = self.area.get_selected_abs()
                if os.path.isdir(abspath):
                    self.chdir(abspath)
                else:
                    curses.flash()

            elif self.ch == curses.KEY_LEFT:
                self.chdir(
                    os.path.dirname(self.area.abspath)
                )

            if self.ch != -1:
                self.refresh_scr()

            if self.kill:
                break

        self.stdscr.clear()

    def cancel(self):
        self.kill = True

if __name__ == "__main__":

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

    print "##############"
    for item in main.checked:
        print item
