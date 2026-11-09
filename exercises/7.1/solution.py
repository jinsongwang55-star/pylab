"""7.1 参考答案：用元类实现插件自动注册。"""


class PluginMeta(type):
    registry = {}

    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        if not bases:
            return cls
        key = getattr(cls, "key", None)
        if not isinstance(key, str) or not key:
            raise TypeError(f"{name} 必须定义非空字符串 key")
        if key in mcls.registry:
            raise ValueError(f"重复的 key: {key}")
        mcls.registry[key] = cls
        return cls


class Plugin(metaclass=PluginMeta):
    key = ""
