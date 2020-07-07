import curses
import logging
from abc import ABCMeta, abstractmethod
from typing import Any, List
from .component import Component
from .listener import ListenerList


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


class DummyTreeModel(TreeModel):
    """
    Dummy implementation
    """

    def get_root(self):
        return "Root"

    def get_child_count(self, parent):
        return 0

    def get_child(self, parent, index):
        return None

    def get_item_at(self, path):
        return self.get_root() if not path else None

    def remove(self, path):
        pass

    def add(self, path, **data):
        return None


class TreeView(Component):
    """
    Tree view
    """

    def __init__(self):
        super().__init__()
        self._model = DummyTreeModel()
        self._current_path = []
        self._select_listeners = ListenerList(self)
        self._sw = None

    def add_select_listener(self, listener):
        self._select_listeners += listener

    def remove_select_listener(self, listener):
        self._select_listeners -= listener

    def set_model(self, model):
        self._model = model
        self._calculate_size()
        self._do_update_view()

    def get_model(self):
        return self._model

    model = property(get_model, set_model)

    def _calculate_size(self):
        w, h = self._get_node_size(self.model.get_root(), 0)
        return w, h

    def _get_node_size(self, node, level):
        width = len(str(node)) + level + 1
        height = 1
        for i in range(self.model.get_child_count(node)):
            child_width, child_height = self._get_node_size(
                self.model.get_child(node, i), level + 1
            )
            width = max(width, child_width)
            height += child_height

        return width, height + 1

    def parent_changed(self):
        r = self.bounds
        w, h = self._calculate_size()
        w = max(w, r.w - 2)
        logging.info(f"{w},{h}")
        self._sw = curses.newpad(h, w)

    def get_current_path(self):
        return list(self._current_path)

    current_path = property(get_current_path)

    def remove(self, path):
        self.model.remove(path)
        self._current_path = self._current_path[:-1]
        self.update_view()

    def add_child(self, path, **kwargs):
        index = self.model.add(path, **kwargs)
        self._current_path += [index]
        self.update_view()

    def on_key_press(self, ch):
        if ch == curses.KEY_DOWN:
            self._move_down()
        elif ch == curses.KEY_UP:
            self._move_up()
        elif ch == curses.KEY_LEFT:
            self._move_left()
        elif ch == curses.KEY_RIGHT:
            self._move_right()
        elif ch in [curses.KEY_ENTER, 13]:
            self._select_listeners(self._current_path)

    def _move_left(self):
        if self._current_path:
            self._current_path = self._current_path[0:-1]
            self.update_view()

    def _move_right(self):

        item = self._model.get_item_at(self._current_path)
        if self._model.get_child_count(item):
            self._current_path.append(0)
            self.update_view()

    def _move_up(self):
        if self._current_path:
            parent_path = self._current_path[0:-1]
            current_index = self._current_path[-1]
            if current_index > 0:
                current_index -= 1
                self._current_path = parent_path + [current_index]
                self.update_view()

    def _move_down(self):
        if self._current_path:
            parent_path = self._current_path[0:-1]
            current_index = self._current_path[-1]
            parent = self._model.get_item_at(parent_path)
            count = self._model.get_child_count(parent)
            if count and current_index < count - 1:
                current_index += 1
                self._current_path = parent_path + [current_index]
                self.update_view()

    def update_view(self):
        self._w.erase()
        if self.has_focus():
            self._w.attron(curses.A_REVERSE)
        self._w.border()
        if self.has_focus():
            self._w.attroff(curses.A_REVERSE)
        self._w.refresh()
        if self._sw:
            _, selection_y = self._write_tree(0, 0, self._model.get_root(), [])
            bounds = self.bounds
            area_height = bounds.h - 2
            offset_y = int(selection_y / area_height) * area_height
            self._sw.refresh(
                offset_y, 0, bounds.y + 1, bounds.x + 1, area_height + 1, bounds.w - 2
            )

    def _write_tree(self, level, y, item, path):
        count = self._model.get_child_count(item)

        char = curses.ACS_TTEE if count > 0 else curses.ACS_HLINE

        attrs = []

        selection_y = 0

        if path == self._current_path:
            attrs = [curses.A_REVERSE]
            selection_y = y

        bounds = self.bounds

        self._sw.addch(y, level, char)

        item_str = str(item)

        self._sw.addstr(y, level + 1, item_str, *attrs)

        ypos = 1
        for i in range(count):
            if i < count - 1:
                self._sw.addch(y + ypos, level, curses.ACS_LTEE)
            else:
                self._sw.addch(y + ypos, level, curses.ACS_LLCORNER)
            size, new_selection_y = self._write_tree(
                level + 1, y + ypos, self._model.get_child(item, i), path + [i]
            )
            if i < count - 1:
                for n in range(1, size):
                    self._sw.addch(y + ypos + n, level, curses.ACS_VLINE)
            ypos += size

            if new_selection_y:
                selection_y = new_selection_y

        return ypos, selection_y
