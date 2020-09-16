import curses
from abc import ABCMeta, abstractmethod
from typing import Any
import logging
from .base import Rectangle


class Component(metaclass=ABCMeta):
    """
    Base component class
    """

    def __init__(self):
        self._rect = Rectangle(0, 0, 1, 1)
        self._parent = None
        self._w = None

    def set_parent(self, parent):
        self._parent = parent
        self._do_update_view()
        self.parent_changed()

    def get_parent(self):
        return self._parent

    parent = property(get_parent, set_parent)

    def get_preferred_size(self):
        return (1, 1)

    preferred_size = property(get_preferred_size)

    def parent_changed(self):
        pass

    def drop_window(self):
        self._w = None

    def refresh(self):
        self._check_w()
        self._do_update_view()

    def set_bounds(self, x, y, w, h):
        new_rect = Rectangle(x, y, w, h)
        old_rect = self._rect
        self._rect = new_rect
        if self._w:
            if old_rect.pos != new_rect.pos:
                self._w.mvwin(*tuple(new_rect.pos))
            if old_rect.size != new_rect.size:
                self._w.resize(*tuple(new_rect.size))
        self._do_update_view()

    def get_bounds(self):
        return self._rect

    bounds = property(get_bounds, set_bounds)

    @property
    def usable_area(self):
        return tuple(self._rect)

    def update_view(self):
        pass

    def on_key_press(self, key):
        pass

    def has_focus(self):
        return self._parent and self._parent.is_focused(self)

    def is_focusable(self):
        return True

    def _check_w(self):
        if not self._w:
            logging.info(f"{self}")
            self._w = self._parent._w.derwin(*self._rect)

    def _do_update_view(self):
        if self._parent:
            self._check_w()
            self.update_view()
