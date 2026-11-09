"""7.4 参考答案：用描述符与元类实现迷你 ORM 的模型层。"""


class Field:
    def __init__(self, type_, default=None):
        self.type = type_
        self.default = default
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name, self.default)

    def __set__(self, instance, value):
        if value is not None:
            if self.type is int and isinstance(value, bool):
                raise TypeError(f"{self.name} 必须是 int，不能是 bool")
            if not isinstance(value, self.type):
                raise TypeError(f"{self.name} 必须是 {self.type.__name__}")
        instance.__dict__[self.name] = value


class ModelMeta(type):
    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        fields = {}
        for base in bases:
            fields.update(getattr(base, "_fields", {}))
        fields.update(
            {key: value for key, value in namespace.items() if isinstance(value, Field)}
        )
        cls._fields = fields
        return cls


class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs):
        for field_name, field in self._fields.items():
            if field_name in kwargs:
                setattr(self, field_name, kwargs.pop(field_name))
            else:
                setattr(self, field_name, field.default)
        if kwargs:
            raise TypeError(f"未知字段: {', '.join(kwargs)}")

    def to_dict(self):
        return {name: getattr(self, name) for name in self._fields}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
