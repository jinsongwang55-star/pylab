"""7.2 参考答案：__slots__ 与弱引用缓存。"""

import weakref


class Point:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y


class WeakCache:
    def __init__(self):
        self._data = weakref.WeakValueDictionary()

    def put(self, key, value):
        self._data[key] = value

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __len__(self):
        return len(self._data)
