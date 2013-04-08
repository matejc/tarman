import sys
sys.path.append("/home/matej/Dropbox/matej/workarea/pys/tarman/src")

from tarman.storage import Checked
from tarman.storage import ViewArea

import curses
import traceback
import os
import argparse


class Main(object):

    def __init__(self, mainscr, stdscr, directory):
        self.header_lns = 1
        self.mainscr = mainscr
        self.stdscr = stdscr
        self.kill = False
        self.ch = -1
        self.directory = os.path.abspath(directory)
        self.checked = Checked(self.directory)
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

    def refresh_scr(self):
        self.stdscr.clear()

        iitem = 0
        for item in self.area:
            i, name, check = item
            self.stdscr.addstr(
                iitem, 0, "[{0}] ... {1}".format(
                    '*' if check else ' ',
                    name
                )
            )
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
                self.header()

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
