from .generic import GenericHandler
from .kv2 import KV2Handler
from .identity import IdentityHandler


class HandlerInfo:
    def __init__(self, type, version=None):
        self.type = type
        self.version = version

    def __eq__(self, other):
        return self.type == other.type and self.version == other.version

    def __hash__(self):
        return hash(f"{self.type}{self.version}")


_DEFAULT = HandlerInfo("generic")
_HANDLERS = {
    _DEFAULT: GenericHandler,
    HandlerInfo("kv", "2"): KV2Handler,
    HandlerInfo("identity"): IdentityHandler,
}


def _get_handler_type(backend):
    info = HandlerInfo(
        backend.info.get("type"), (backend.info.get("options", {}) or {}).get("version")
    )
    if not info in _HANDLERS:
        return _HANDLERS[_DEFAULT]
    return _HANDLERS[info]


def get_handler(client, backend_info):
    return _get_handler_type(backend_info)(client, backend_info)
