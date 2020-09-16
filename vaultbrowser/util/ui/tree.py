from .view import View
from abc import ABCMeta, abstractmethod
from typing import Any, List
from .listener import ListenerHandler
from vaultbrowser.util import ansi, kbd

_ICON_OPEN= '▾'
_ICON_CLOSED= '▸'

class TreeModel(metaclass=ABCMeta):
    """
    Tree Model interface
    """

    @abstractmethod
    def get_root(self) -> Any:
        pass

    @abstractmethod
    def get_child_count(self, parent: Any) -> int:
        pass

    @abstractmethod
    def get_child(self, parent: Any, index: int) -> Any:
        pass

    @abstractmethod
    def get_item_at(self, path: List) -> Any:
        pass

    @abstractmethod
    def remove(self, path: List):
        pass

    @abstractmethod
    def add(self, path, **data):
        pass

class TreeView(View):
    _model = None
    _current_node = None
    def __init__(self, rect=None, model=None):
        super().__init__(rect)
        self._scroll_y = 0
        self._current_y = 0
        self._on_select = ListenerHandler(self)
        self.model = model

    def set_model(self, model):
        self._model = model
        if self._model:
            self._current_node = model.get_root()
        else:
            self._current_path = None

    def get_model(self):
        return self._model

    model = property(get_model, set_model)

    @property
    def on_select(self):
        return self._on_select

    def update(self):
        buff = ansi.begin()
        buff.gotoxy(self._rect.x, self._rect.y)

        if self._current_node:
            if self._current_y == 0:
                buff.underline()
            buff.write(str(self._current_node)).reset()
            
            max_children = min(self._rect.height-1,self._model.get_child_count(self._current_node))

            for i in range(max_children):
                buff.gotoxy(self._rect.x+2,self._rect.y+1+i)
                if i + 1 + self._scroll_y == self._current_y:
                    buff.underline()
                buff.write(str(self._model.get_child(self._current_node, i)))
                buff.reset()
        buff.put()

    def _get_current_item(self):
        pass

    def on_key_press(self, key):
        if key == kbd.KEY_UP:
            if self._current_y > 0:
                self._current_y-= 1
                self.queue_update()
        elif key == kbd.KEY_DOWN:
            self._current_y += 1
            self.queue_update()
        elif key == kbd.KEY_LEFT:
            pass
        elif key == kbd.KEY_ENTER:
            pass
