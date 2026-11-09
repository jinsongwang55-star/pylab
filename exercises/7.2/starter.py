"""7.2 练习：__slots__ 与弱引用缓存。"""

import weakref


class Point:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        raise NotImplementedError("删掉这一行，开始实现")


class WeakCache:
    def __init__(self):
        raise NotImplementedError("删掉这一行，开始实现")

    def put(self, key, value):
        raise NotImplementedError("删掉这一行，开始实现")

    def get(self, key, default=None):
        raise NotImplementedError("删掉这一行，开始实现")

    def __len__(self):
        raise NotImplementedError("删掉这一行，开始实现")
