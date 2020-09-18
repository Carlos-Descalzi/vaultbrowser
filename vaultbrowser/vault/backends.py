from vaultbrowser.util.ui import ListModel
import logging

class BackendItem:
    def __init__(self, name, info):
        self.name = name
        self.info = info

    def __str__(self):
        return self.name

class BackendListModel(ListModel):
    
    def __init__(self):
        super().__init__()
        self._client = None
        self._backends = []

    def set_client(self, client):
        self._client = client
        logging.info("2")
        self._update()

    def get_client(self):
        return self._client

    client = property(get_client, set_client)

    def _update(self):
        if self._client:
            self._backends = [
                BackendItem(k,v)
                for k,v in self._client.sys.list_mounted_secrets_engines().items()
            ]
        else:
            self._backends = []
        self.notify_list_changed()

    def get_item_count(self):
        return len(self._backends)

    def get_item(self, index):
        return self._backends[index]
