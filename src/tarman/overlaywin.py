
from tarman.exceptions import NotImplemented

import curses
import os
import threading
import time


class OverlayWin():

    def __init__(self, main):
        self.main = main

    def show(self, *args):
        raise NotImplemented()

    def close(self):
        raise NotImplemented()


class TextWin(OverlayWin):

    def show(self, *args):
        text = args[0]

        lines, columns = self.main.stdscr.getmaxyx()

        textdata = text.split('\n')
        height = len(textdata) + 4
        width = max([len(s) for s in textdata]) + 4

        self.showing = True
        self.exitstatus = -1
        self.newwin = self.main.stdscr.derwin(
            height, width,
            (lines / 2) - (height / 2), (columns / 2) - (width / 2)
        )
        self.newwin.clear()
        self.newwin.border()
        self.newwin.touchwin()
        self.newwin.refresh()

        for i in range(len(textdata)):
            self.newwin.addstr(i + 2, 2, textdata[i])

        while self.showing:
            self.ch = self.newwin.getch()
            if self.ch:
                self.close()

        self.main.mainscr.touchwin()
        self.main.mainscr.refresh()
        self.main.stdscr.touchwin()
        self.main.stdscr.refresh()
        self.main.refresh_scr()

    def close(self):
        self.showing = False


class QuestionWin(OverlayWin):

    def show(self, *args):
        text = args[0]

        self.exitstatus = -1
        lines, columns = self.main.stdscr.getmaxyx()

        text += "\n\nPress ESC to Cancel or ENTER for Ok!"

        textdata = text.split('\n')
        height = len(textdata) + 4
        width = max([len(s) for s in textdata]) + 4

        self.showing = True
        self.exitstatus = -1
        self.newwin = self.main.stdscr.derwin(
            height, width,
            (lines / 2) - (height / 2), (columns / 2) - (width / 2)
        )
        self.newwin.clear()
        self.newwin.border()
        self.newwin.touchwin()
        self.newwin.refresh()

        for i in range(len(textdata)):
            self.newwin.addstr(i + 2, 2, textdata[i])

        while self.showing:
            self.ch = self.newwin.getch()
            if self.ch in [27]:
                self.close()
                self.exitstatus = 1
            elif self.ch in [10, 13]:
                self.close()
                self.exitstatus = 0

        self.main.mainscr.touchwin()
        self.main.mainscr.refresh()
        self.main.stdscr.touchwin()
        self.main.stdscr.refresh()
        self.main.refresh_scr()

        return self.exitstatus

    def close(self):
        self.showing = False


class WorkWin(OverlayWin):

    def show(self, *args):
        text = args[0]

        lines, columns = self.main.stdscr.getmaxyx()
        self.showing = True
        self.exitstatus = -1
        w = columns / 2
        self.newwin = self.main.stdscr.derwin(
            3, w, (lines / 2) - (3 / 2), w - (columns / 4)
        )
        self.newwin.clear()
        self.newwin.nodelay(1)
        curses.curs_set(0)
        self.text = text
        self.newwin.border()
        self.newwin.addstr(1, 1, text)
        self.newwin.touchwin()
        self.newwin.refresh()

        def run(handle, w):
            i = 1
            while handle.showing:
                handle.newwin.chgat(1, i, 1, curses.A_REVERSE)
                handle.newwin.refresh()
                time.sleep(0.1)
                handle.newwin.chgat(1, i, 1, curses.A_NORMAL)
                handle.newwin.refresh()
                i += 1
                if i == w - 1:
                    i = 1

            self.newwin.nodelay(0)
            curses.curs_set(1)
            handle.main.mainscr.touchwin()
            handle.main.mainscr.refresh()
            handle.main.stdscr.touchwin()
            handle.main.stdscr.refresh()
            handle.main.refresh_scr()

        t = threading.Thread(target=run, args=(self, w))
        t.setDaemon(True)
        t.start()

    def close(self):
        self.showing = False


class PathWin(OverlayWin):

    def show(self, *args):
        """
        exitstatus:
            -2: path not exists
            -1: internal error
             0: all ok
             1: canceled
        """
        text = args[0]
        lines, columns = self.main.stdscr.getmaxyx()
        self.showing = True
        self.exitstatus = -1
        self.newwin = self.main.stdscr.derwin(
            5, columns, (lines / 2) - (5 / 2), 0
        )
        self.text = text
        self.newwin.clear()
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
            while handle.showing and getattr(handle, 'textwin', None):
                handle.refresh_exists()
                time.sleep(0.1)

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

        s = "  Exists  " if exists else "Not Exists"

        self.newwin.touchwin()
        self.newwin.refresh()

        if self.main.color:
            self.newwin.addstr(
                1,
                self.newwin.getmaxyx()[1] / 2 - len(s) / 2,
                s,
                self.main.attr_wright if exists else self.main.attr_wrong
            )
        else:
            self.newwin.addstr(
                1,
                self.newwin.getmaxyx()[1] / 2 - len(s) / 2,
                s,
            )

        self.textwin.touchwin()
        self.textwin.refresh()

    def close(self):
        if self.textbox:  # force window to close instantaneously
            self.textbox.do_command = lambda x: False
        self.showing = False
