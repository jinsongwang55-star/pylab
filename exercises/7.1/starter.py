"""7.1 练习：用元类实现插件自动注册。"""


class PluginMeta(type):
    registry = {}

    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        # TODO: 校验 key 并注册子类
        return cls


class Plugin(metaclass=PluginMeta):
    key = ""
