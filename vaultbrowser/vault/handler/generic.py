from .handler import BackendHandler
from pathlib import PurePath
import logging


class GenericHandler(BackendHandler):
    """
    Handler for Generic and Key/Value v.1 backends.
    """
    def _real_path(self, path):
        return str(PurePath(self._backend_info.name, path))

    def read(self, path):
        return self._client.read(self._real_path(path))

    def read_value(self, path):
        value = self.read(path)
        if value:
            return value['data']
        return value

    def list(self, path):
        entry = self._client.list(self._real_path(path))
        return (entry or {}).get("data", {}).get("keys", [])

    def write(self, path, data):
        self._client.write(self._real_path(path), **data)

    def delete(self, path):
        self._client.delete(self._real_path(path))
