from cdtui import ListModel


class ServicesListModel(ListModel):
    """
    Services list model.
    """
    def __init__(self, services=[]):
        super().__init__()
        self._services = services

    def _on_connect(self, service):
        self.notify_list_changed()

    def _on_error(self, service, error):
        self.notify_list_changed()

    def set_services(self, services):
        if self._services:
            for service in self._services:
                service.on_connect.remove(self._on_connect)
                service.on_connect_error.remove(self._on_connect)
        self._services = services
        for service in self._services:
            service.on_connect.add(self._on_connect)
            service.on_connect_error.add(self._on_error)
        self.notify_list_changed()

    def get_services(self):
        return self._services

    services = property(get_services, set_services)

    def get_item_count(self):
        return len(self._services)

    def get_item(self, index):
        return self._services[index]
