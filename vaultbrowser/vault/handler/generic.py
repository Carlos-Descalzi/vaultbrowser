from .handler import BackendHandler
from pathlib import PurePath
import logging


class GenericHandler(BackendHandler):
    def _real_path(self, path):
        return str(PurePath(self._backend_info.name, path))

    def read(self, path):
        return self._client.read(self._real_path(path))

    def list(self, path):
        entry = self._client.list(self._real_path(path))
        return (entry or {}).get("data", {}).get("keys", [])

    def write(self, path, data):
        self._client.write(self._real_path(path), data)

    def delete(self, path):
        self._client.delete(self._real_path(path))
