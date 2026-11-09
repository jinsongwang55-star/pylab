"""5.0 练习：实现一个极简路由器。"""


class Router:
    def __init__(self):
        self.routes = []

    def add(self, method, pattern, handler):
        raise NotImplementedError("删掉这一行，开始实现")

    def dispatch(self, method, path):
        """返回 (status_code, payload)。"""
        raise NotImplementedError("删掉这一行，开始实现")
