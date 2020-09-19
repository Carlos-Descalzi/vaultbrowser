import logging
from .handler import BackendHandler


class KV2Handler(BackendHandler):
    @property
    def _mount_point(self):
        return self._backend_info.name

    def write(self, path, value):
        self._client.secrets.kv.v2.create_or_update_secret(
            mount_point=self._mount_point, path=path, secret=value
        )

    def read(self, path):
        return self._client.secrets.kv.v2.read_secret_version(
            mount_point=self._mount_point, path=path
        )

    def list(self, path):
        result = self._client.secrets.kv.v2.list_secrets(
            mount_point=self._mount_point, path=path
        )
        return result.get("data", {}).get("keys", [])

    def delete(self, path):
        self._client.secrets.kv.v2.delete_latest_version_of_secret(
            mount_point=self._mount_point, path=path
        )
