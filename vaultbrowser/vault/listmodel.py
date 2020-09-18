from vaultbrowser.util.ui import ListModel
import logging
import hvac
import os

class Node:
    def __init__(self, client, parent, name):
        self._client = client
        self._parent = parent
        self._name = name
        self._children = None if name[-1] == "/" else []
        logging.info(f'Path:{self.path}')

    @property
    def child_count(self):
        return len(self.children)

    @property
    def path(self):
        path = []
        node = self
        while node:
            path.append(node.name.replace('/',''))
            node = node.parent

        return "/".join(reversed(path))

    @property
    def children(self):
        if self._children is None:
            children = []
            result = self._client.list(self.path)
            for item in result["data"]["keys"]:
                children.append(Node(self._client, self, item))
            self._children = sorted(children, key=lambda x:x.name)
        return self._children

    def get_value(self):
        return self._client.read(self.path)

    def set_value(self, value):
        self._client.write(self.path, **value)

    value = property(get_value, set_value)

    @property
    def leaf(self):
        return self._name[-1] != '/'

    @property
    def parent(self):
        return self._parent

    @property
    def name(self):
        return self._name

    def __str__(self):
        return self.name

    def remove(self):
        self._client.delete(self.path)

    def add_child(self, name, data):
        new_path = "/".join([self.path, name])
        self._client.write(new_path, **data)
        self._children.append(Node(self._client,self , name))
        return len(self._children) - 1

class VaultListModel(ListModel):
    def __init__(self):
        super().__init__()
        #url = os.environ["VAULT_ADDR"]
        #token = os.environ["VAULT_TOKEN"]
        #self._client = hvac.Client(url, token)
        self._client = None
        self._backend = None
        self._root = None
        self._current = None

    def set_client(self, client):
        old_client = self._client
        self._client = client
        if old_client == client:
            self._backend = None
        self._update()

    def get_client(self):
        return self._client

    client = property(get_client, set_client)

    def set_backend(self, backend):
        self._backend = backend
        self._update()

    def get_backend(self):
        return self._backend

    backend = property(get_backend, set_backend)

    def _update(self):
        if self._client and self._backend:
            self._root = Node(self._client, None, self._backend+"/")
            self._current = self._root
        else:
            self._root = None
            self._current = None
        self.notify_list_changed()

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
            index-=1
        return self._current.children[index]

