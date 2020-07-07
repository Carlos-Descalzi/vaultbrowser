import curses
from abc import ABCMeta, abstractmethod
from typing import Any
import logging


class Size:
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def __iter__(self):
        return iter((self.h, self.w))

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.w == other.w
            and self.h == other.h
        )


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __iter__(self):
        return iter((self.y, self.x))

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.x == other.x
            and self.y == other.y
        )


class Rectangle:
    def __init__(self, x, y, w, h):
        self._pos = Point(x, y)
        self._size = Size(w, h)

    @property
    def pos(self):
        return self._pos

    @property
    def size(self):
        return self._size

    @property
    def x(self):
        return self._pos.x

    @property
    def y(self):
        return self._pos.y

    @property
    def w(self):
        return self._size.w

    @property
    def h(self):
        return self._size.h

    def __iter__(self):
        return iter(list(self._size) + list(self._pos))

    def __str__(self):
        return f"Rectangle:({self.x},{self.y},{self.w},{self.h})"

    def __repr__(self):
        return str(self)
