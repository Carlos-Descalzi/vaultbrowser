from .component import Component
import curses
import logging


class Label(Component):
    def __init__(self, text):
        super().__init__()
        self._text = text
        self.set_bounds(0, 0, 40, 1)
        self._attr = None

    def set_attr(self, attr):
        self._attr = attr

    def get_attr(self):
        return self._attr

    attr = property(get_attr, set_attr)

    def set_text(self, text):
        self._text = text
        self.update_view()

    def get_text(self):
        return self._text

    text = property(get_text, set_text)

    def is_focusable(self):
        return False

    def update_view(self):
        self._w.erase()
        h, w = self._rect.size
        text = self._text + (" " * (w - (1 + len(self._text))))

        attr = [self._attr] if self._attr else []

        self._w.addstr(0, 0, text, *attr)
        self._w.refresh()
