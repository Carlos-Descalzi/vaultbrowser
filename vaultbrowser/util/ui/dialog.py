import logging
from .view import View
from vaultbrowser.util import ansi
from .base import Rect
from .input import Input
from collections import OrderedDict


class Option:
    def __init__(self, label, handler):
        self.label = label
        self.handler = handler


class QuestionDialog(View):
    def __init__(self, title, message, options=[]):
        super().__init__()
        self._title = title
        self._message = message
        self._options = OrderedDict([(k, Option(l, f)) for k, l, f in options])
        self._options_text = " ".join(
            [f"{k}: {v.label}" for k, v in self._options.items()]
        )
        self._rect = Rect(
            0, 0, max(map(len, [self._title, self._message, self._options_text])) + 2, 5
        )

    def update(self):

        options_text = (
            " " * (self._rect.width - len(self._options_text))
        ) + self._options_text

        (
            ansi.begin()
            .reverse()
            .gotoxy(self._rect.x, self._rect.y)
            .writefill(self._title, self._rect.width)
            .reset()
            .gotoxy(self._rect.x, self._rect.y + 1)
            .writefill("", self._rect.width)
            .gotoxy(self._rect.x, self._rect.y + 2)
            .writefill(self._message, self._rect.width)
            .gotoxy(self._rect.x, self._rect.y + 3)
            .writefill("", self._rect.width)
            .gotoxy(self._rect.x, self._rect.y + 4)
            .reverse()
            .writefill(self._options_text, self._rect.width)
            .reset()
        ).put()

    def on_key_press(self, input_key):
        chr_key = chr(input_key)
        if chr_key in self._options:
            self._options[chr_key].handler()


class InputDialog(View):
    def __init__(self, title, on_confirm, disallowed_chars=""):
        super().__init__()
        self._title = title
        self._input = Input(disallowed_chars=disallowed_chars)
        self._input.on_enter.add(self._on_enter)
        self._on_confirm = on_confirm
        self._rect = Rect(0, 0, 40, 5)

    def _on_enter(self, field, input_text):
        self._on_confirm(input_text)

    def update(self):
        (
            ansi.begin()
            .gotoxy(self._rect.x, self._rect.y)
            .reverse()
            .writefill(self._title, self._rect.width)
            .gotoxy(self._rect.x, self._rect.y + 4)
            .writefill("Enter: Accept, Esc: Cancel", self._rect.width)
            .reset()
        ).put()
        r = self._rect.copy()
        r.y += 2
        self._input.rect = r
        self._input.update()

    def on_key_press(self, input_key):
        self._input.on_key_press(input_key)
