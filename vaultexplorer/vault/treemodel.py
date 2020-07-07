from ..tui import TreeModel
import hvac
import os


class Node:
    def __init__(self, client, path):
        self._client = client
        self._path = path
        self._children = None if path[-1] == "/" else []

    @property
    def child_count(self):
        return len(self.children)

    @property
    def children(self):
        if self._children is None:
            self._children = []
            result = self._client.list(self._path)
            for item in result["data"]["keys"]:
                self.children.append(Node(self._client, self._path + item))
        return self._children

    def value(self):
        return self._client.read(self._path)

    def set_value(self, value):
        self._client.write(self._path, **value)

    def __str__(self):
        path = self._path
        if path[-1] == "/":
            path = path[0:-1]
        return path.split("/")[-1]

    def remove(self):
        self._client.delete(self._path)

    def add_child(self, data):
        new_path = "/".join([self._path, data["name"]])
        self._client.write(new_path, **data["data"])
        self._children.append(Node(self._client, new_path))
        return len(self._children) - 1


class VaultTreeModel(TreeModel):
    def __init__(self):
        url = os.environ["VAULT_ADDR"]
        token = os.environ["VAULT_TOKEN"]
        self._client = hvac.Client(url, token)
        self._root = Node(self._client, "secret/")

    def get_root(self):
        return self._root

    def get_child_count(self, parent):
        return parent.child_count

    def get_child(self, parent, index):
        return parent.children[index]

    def get_item_at(self, path):
        item = self._root
        while path:
            index = path[0]
            path = path[1:]
            item = item.children[index]

        return item

    def remove(self, path):
        item = self.get_item_at(path)
        item.remove()
        parent = self.get_item_at(path[:-1])
        parent.children.remove(item)

    def add(self, path, **data):
        item = self.get_item_at(path)
        return item.add_child(data)
