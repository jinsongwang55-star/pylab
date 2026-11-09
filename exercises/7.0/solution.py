"""7.0 参考答案：实现带校验的数据描述符 Positive。"""


class Positive:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return instance.__dict__[self.name]
        except KeyError:
            raise AttributeError(f"{self.name} 尚未赋值") from None

    def __set__(self, instance, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{self.name} 必须是数字")
        if value <= 0:
            raise ValueError(f"{self.name} 必须大于 0")
        instance.__dict__[self.name] = value
