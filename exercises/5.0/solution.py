"""5.0 参考答案：实现一个极简路由器。"""


class Router:
    def __init__(self):
        self.routes = []

    def add(self, method, pattern, handler):
        segments = pattern.strip("/").split("/")
        self.routes.append((method.upper(), segments, handler))

    def dispatch(self, method, path):
        actual = path.strip("/").split("/")
        path_matched = False
        for route_method, pattern, handler in self.routes:
            params = self._match(pattern, actual)
            if params is None:
                continue
            path_matched = True
            if route_method != method.upper():
                continue
            return 200, handler(**params)
        if path_matched:
            return 405, {"error": "Method Not Allowed"}
        return 404, {"error": "Not Found"}

    @staticmethod
    def _match(pattern, segments):
        if len(pattern) != len(segments):
            return None
        params = {}
        for expected, value in zip(pattern, segments):
            if expected.startswith("{") and expected.endswith("}"):
                params[expected[1:-1]] = value
            elif expected != value:
                return None
        return params
