

class BackendHandler:
    def __init__(self, client, backend_info):
        self._client = client
        self._backend_info = backend_info

    def write(self, path, value):
        pass

    def read(self, path):
        pass

    def list(self, path):
        pass

    def delete(self, path):
        pass

class GenericHandler(BackendHandler):
    pass

class KV2Handler(BackendHandler):
    pass


def get_handler(client, backend_info):
    pass
