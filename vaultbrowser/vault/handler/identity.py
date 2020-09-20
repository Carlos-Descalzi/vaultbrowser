from .handler import BackendHandler
from pathlib import PurePath
import logging


class IdentityHandler(BackendHandler):
    """
    Handler for identity backend
    """
    def _real_path(self, path):
        return str(PurePath(self._backend_info.name, path))

    def read(self, path):
        return self._client.read(self._real_path(path))

    def list(self, path):
        logging.info(f"list {path}")
        if path in ["", "/"]:
            return [
                "entity/",
                "entity-alias/",
                "group/",
                "group-alias/",
                "token/",
                "lookup/",
            ]
        elif path == "entity/":
            entry = self._client.secrets.identity.list_entities()
        elif path == "entity-alias/":
            entry = self._client.secrets.identity.list_entity_aliases()
        elif path == "group/":
            entry = client.secrets.identity.list_groups()
        elif path == "group-alias/":
            entry = client.secrets.identity.list_group_aliases()
        elif path == "token/":
            entry = None
        elif path == "lookup/":
            entry = None
        else:
            entry = None

        return (entry or {}).get("data", {}).get("keys", [])

    def write(self, path, data):
        self._client.write(self._real_path(path), data)

    def delete(self, path):
        self._client.delete(self._real_path(path))
