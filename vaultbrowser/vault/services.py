from vaultbrowser.util.ui import ListModel


class ServicesListModel(ListModel):

    def __init__(self, services=[]):
        super().__init__()
        self._services = services

    def set_services(self, services):
        self._services = services
        self.notify_list_changed()

    def get_services(self):
        return self._services

    services = property(get_services, set_services)

    def get_item_count(self):
        return len(self._services)

    def get_item(self, index):
        return self._services[index]
