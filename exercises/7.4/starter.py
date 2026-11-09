"""7.4 综合练习：用描述符与元类实现迷你 ORM 的模型层。"""


class Field:
    def __init__(self, type_, default=None):
        self.type = type_
        self.default = default
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        raise NotImplementedError("删掉这一行，开始实现")

    def __set__(self, instance, value):
        raise NotImplementedError("删掉这一行，开始实现")


class ModelMeta(type):
    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        # TODO: 收集 Field 到 cls._fields
        return cls


class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs):
        raise NotImplementedError("删掉这一行，开始实现")

    def to_dict(self):
        raise NotImplementedError("删掉这一行，开始实现")

    @classmethod
    def from_dict(cls, data):
        raise NotImplementedError("删掉这一行，开始实现")
