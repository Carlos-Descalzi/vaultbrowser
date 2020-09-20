from cdtui import ListModel
import logging
import traceback
import hvac
import os
from .handler import get_handler


class Node:
    def __init__(self, model, parent, name):
        self._model = model
        self._parent = parent
        self._name = name
        self._children = None  # if name and name[-1] == "/" else []
        logging.info(f"Path:{self.path}")

    @property
    def child_count(self):
        return len(self.children)

    @property
    def path(self):
        path = []
        node = self
        while node:
            if node.name:
                path.append(node.name.replace("/", ""))
            node = node.parent

        return "/".join(reversed(path))

    @property
    def children(self):
        try:
            if self._children is None:
                children = []
                result = self._model._handler.list(self.path)
                self._children = sorted(
                    [Node(self._model, self, i) for i in result], key=lambda x: x.name
                )
            return self._children
        except Exception as e:
            logging.error(f"{e} - {traceback.format_exc()}")
            return self._children

    def get_value(self):
        return self._model._handler.read(self.path)

    def set_value(self, value):
        self._model._handler.write(self.path, value)

    value = property(get_value, set_value)

    @property
    def data(self):
        return self._model._handler.read_value(self.path)

    @property
    def leaf(self):
        return self._name[-1] != "/" if self._name else False

    @property
    def parent(self):
        return self._parent

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self.name

    def remove(self):
        self._model._handler.delete(self.path)

    def add_child(self, name, data):
        new_path = "/".join([self.path, name])
        logging.info(f"New path:{new_path}, value:{data}")
        self._model._handler.write(new_path, data)
        self._children.append(Node(self._model, self, name))
        self._model.notify_list_changed()

class VaultListModel(ListModel):
    """
    List model for vault contents.
    This model works pretty much like a tree navigator.
    """
    def __init__(self):
        super().__init__()
        self._client = None
        self._handler = None
        self._backend = None
        self._root = None
        self._current = None

    def set_client(self, client):
        old_client = self._client
        self._client = client
        if old_client == client:
            self._backend = None
            self._handler = None
        self._update()

    def get_client(self):
        return self._client

    client = property(get_client, set_client)

    def set_backend(self, backend):
        if backend:
            self._backend = backend
            self._handler = get_handler(self._client, backend)
        else:
            self._backend = None
            self._handler = None
        self._update()

    def get_backend(self):
        return self._backend

    backend = property(get_backend, set_backend)

    def _update(self):
        try:
            if self._handler:
                self._root = Node(self, None, "")
                self._current = self._root
            else:
                self._root = None
                self._current = None
            self.notify_list_changed()
        except Exception as e:
            logging.error(f"{e} - {traceback.format_exc()}")

    def get_root(self):
        return self._root

    def get_current(self):
        return self._current

    def remove_child(self, item):
        item.remove()
        self._current.children.remove(item)
        self.notify_list_changed()

    def go_to(self, node):
        self._current = node
        self.notify_list_changed()

    def go_up(self):
        self._current = self._current.parent
        self.notify_list_changed()

    @property
    def in_root(self):
        return self._current == self._root

    def get_item_count(self):
        if self._root:
            return self._current.child_count + (0 if self.in_root else 1)
        return 0

    def get_item(self, index):
        if not self.in_root:
            if index == 0:
                return ".."
            index -= 1
        return self._current.children[index]
