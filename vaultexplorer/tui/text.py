from .component import Component
import curses
from curses.textpad import Textbox
import logging


class TextView(Component):
    def __init__(self):
        super().__init__()
        self._editor = None
        self._text = ""
        self._lines = []

    def _max_size(self):
        y, x = len(self._lines) or 1, max([len(l) for l in self._lines] or [1])
        return y, x

    def set_text(self, text):
        self._text = text or ""
        self._lines = []
        lines = self._text.split("\n")
        max_width = self._rect.w - 3
        for line in lines:
            if len(line) < max_width:
                self._lines.append(line)
            else:
                while line:
                    self._lines.append(line[0:max_width])
                    line = line[max_width:]
        self._do_update_view()

    def get_text(self):
        return self._text

    text = property(get_text, set_text)

    def update_view(self):
        self._w.erase()
        if self.has_focus():
            self._w.attron(curses.A_REVERSE)
        self._w.border()
        if self.has_focus():
            self._w.attroff(curses.A_REVERSE)

        n_lines = self._rect.h - 3
        for i in range(min(n_lines, len(self._lines))):
            line = self._lines[i]
            self._w.addstr(i + 1, 1, line)
        self._w.refresh()
