"""7.0 练习：实现带校验的数据描述符 Positive。"""


class Positive:
    def __set_name__(self, owner, name):
        raise NotImplementedError("删掉这一行，开始实现")

    def __get__(self, instance, owner):
        raise NotImplementedError("删掉这一行，开始实现")

    def __set__(self, instance, value):
        raise NotImplementedError("删掉这一行，开始实现")
