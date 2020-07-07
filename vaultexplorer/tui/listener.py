class ListenerList:
    def __init__(self, target):
        self._target = target
        self._listeners = []

    def __iadd__(self, item):
        self._listeners.append(item)
        return self

    def __call__(self, *args, **kwargs):
        for item in self._listeners:
            item(self._target, *args, **kwargs)
