from sets import Set

import curses
import traceback
import os
import argparse


class Main(object):

    def __init__(self, stdscr, directory=None):
        self.stdscr = stdscr
        self.selected = 0
        self.kill = False
        self.ch = -1
        self.checkedfiles = {}
        self.chdir(directory)

    def addcheckedfiles(self):
        s = Set([f[1] for f in self.listfiles if f[0]])
        if not s:
            return
        if self.directory in self.checkedfiles:
            self.checkedfiles[self.directory].update(s)
        else:
            self.checkedfiles[self.directory] = s

    def chdir(self, path, checked_content=False):
        if os.path.isdir(path):
            self.directory = os.path.abspath(path)
        else:
            return
        self.listfiles = \
            [[checked_content, f] for f in sorted(os.listdir(self.directory))]
        self.run(reset_cur=True)

    def run(self, reset_cur=False):
        last = len(self.listfiles) - 1
        h, w = self.stdscr.getmaxyx()

        if self.selected < 0:
            self.selected = 0
        elif self.selected > last:
            self.selected = last

        if self.selected >= h - 1:  # at start
            j = self.selected - h + 1
            y = h - 1
        else:  # further
            j = 0
            y = self.selected

        self.stdscr.clear()
        for i in range(min(last + 1, h)):
            b = self.listfiles[i + j][0]
            self.stdscr.addstr(
                i, 0, "[{0}] {1}".format(
                    "*" if b else " ",
                    self.listfiles[i + j][1][:w]
                )
            )
            i += 1
            if h == i:
                break

        if reset_cur:
            self.stdscr.move(0, 1)
        else:
            self.stdscr.move(y, 1)

    def loop(self):
        while not self.kill:
            self.ch = self.stdscr.getch()

            if self.ch in [ord('q'), 27]:
                self.kill = True

            elif self.ch == curses.KEY_UP:
                self.selected -= 1

            elif self.ch == curses.KEY_DOWN:
                self.selected += 1

            elif self.ch == curses.KEY_PPAGE:
                self.selected -= self.stdscr.getmaxyx()[0] / 2

            elif self.ch == curses.KEY_NPAGE:
                self.selected += self.stdscr.getmaxyx()[0] / 2

            elif self.ch == 32:
                b = self.listfiles[self.selected][0]
                self.listfiles[self.selected][0] = not b

            elif self.ch == ord('e'):
                self.chdir(
                    os.path.join(
                        self.directory, self.listfiles[self.selected][1]
                    ),
                    checked_content=self.listfiles[self.selected][0]
                )

            if self.ch != -1:
                self.run()

            if self.kill:
                break

        self.addcheckedfiles()
        self.stdscr.clear()

    def cancel(self):
        self.kill = True

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Directory.")
    args = parser.parse_args()

    try:
        # Initialize curses
        stdscr = curses.initscr()
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

        main = Main(stdscr, args.directory)
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
    print main.checkedfiles
