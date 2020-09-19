from .util.ui.listener import ListenerHandler
import threading
import hvac
import logging


class Service:
    def __init__(self, name, url, token, verify_tls):
        self._on_connect = ListenerHandler(self)
        self._on_connect_error = ListenerHandler(self)
        self._name = name
        self._url = url
        self._token = token
        self._verify_tls = verify_tls
        self._info = None
        self._connection_thread = None
        self._client = None
        self._error = None

    def connect(self):
        self._connection_thread = threading.Thread(target=self._do_connect, daemon=True)
        self._connection_thread.start()

    @property
    def on_connect(self):
        return self._on_connect

    @property
    def on_connect_error(self):
        return self._on_connect_error

    @property
    def connecting(self):
        return self._connection_thread.is_alive()

    @property
    def error(self):
        return self._error

    @property
    def connected(self):
        return self._client is not None

    @property
    def client(self):
        return self._client

    @property
    def name(self):
        return self._name

    def disconnect(self):
        pass

    def _do_connect(self):
        try:
            logging.info("Creating connection")
            client = hvac.Client(
                url=self._url, token=self._token, verify=self._verify_tls
            )
            client.sys.list_mounted_secrets_engines()
            self._client = client
            self._on_connect()
        except Exception as e:
            logging.error(e)
            self._error = e
            self._on_connect_error(e)
