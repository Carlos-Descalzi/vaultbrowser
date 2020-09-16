import curses
from abc import ABCMeta, abstractmethod
from typing import Any
import logging
import time


class Screen:
    def __init__(self):
        self._running = False
        self._w = curses.initscr()
        curses.noecho()
        self._w.keypad(True)
        curses.cbreak()
        curses.nonl()
        curses.curs_set(False)
        self._w.nodelay(True)
        self._components = []
        self._active = None
        self._keybindings = {}

    def get_size(self):
        return self._w.getmaxyx()

    size = property(get_size)

    def is_focused(self, component):
        return self._active == component

    def focus_next(self):
        index = self._components.index(self._active)

        new_active = None

        while not new_active:
            if index < len(self._components) - 1:
                index += 1
            else:
                index = 0
            if self._components[index].is_focusable():
                new_active = self._components[index]
        self._active = new_active
        self.refresh()

    def add_keybinding(self, key, handler):
        self._keybindings[ord(key)] = handler

    def delete_keybinding(self, key):
        del self._keybindings[ord(key)]

    def focus(self, component):
        self._active = component
        self.refresh()

    def get_focused(self):
        return self._active

    focused = property(get_focused)

    def add(self, component):
        if not self._active:
            self._active = component
        self._components.append(component)
        component.set_parent(self)

    def remove(self, component):
        index = self._components.index(component)
        self._components.pop(index)
        if self._active == component:
            self.focus(self._components[0])
        del component
        self.refresh()

    def add_and_focus(self, component):
        self.add(component)
        self.focus(component)

    def refresh(self):
        self._w.refresh()
        for c in reversed(self._components):
            c.refresh()

    def drop_window(self):
        self._w = None
        for c in self._components:
            c.drop_window()
        curses.endwin()

    def restart(self):
        self._w = curses.initscr()
        self.refresh()

    def run(self):
        self._running = True

        while self._running:
            self._w.refresh()
            ch = self._w.getch()
            if ch != -1:
                if ch in [27, ord("q")]:
                    self._running = False
                elif ch == 9:  # tab
                    self.focus_next()
                elif ch in self._keybindings:
                    self._keybindings[ch]()
                elif self._active:
                    self._active.on_key_press(ch)

            time.sleep(0.1)

        self._w.nodelay(False)
        curses.nocbreak()
        curses.nl()
        curses.curs_set(True)
        curses.echo()
        curses.endwin()
