import logging
from abc import ABCMeta, abstractmethod


class BackendHandler(metaclass=ABCMeta):
    def __init__(self, client, backend_info):
        self._client = client
        self._backend_info = backend_info
        logging.info(self._backend_info)

    @abstractmethod
    def write(self, path, value):
        pass

    @abstractmethod
    def read(self, path):
        pass

    @abstractmethod
    def list(self, path):
        pass

    @abstractmethod
    def delete(self, path):
        pass

