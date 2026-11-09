import solution
from _harness import run


def _reset():
    solution.PluginMeta.registry.clear()


def test_registers_subclass():
    _reset()

    class JsonPlugin(solution.Plugin):
        key = "json"

    assert solution.PluginMeta.registry["json"] is JsonPlugin


def test_registers_multiple():
    _reset()

    class A(solution.Plugin):
        key = "a"

    class B(solution.Plugin):
        key = "b"

    assert solution.PluginMeta.registry == {"a": A, "b": B}


def test_duplicate_key():
    _reset()

    class First(solution.Plugin):
        key = "same"

    try:
        class Second(solution.Plugin):
            key = "same"
    except ValueError:
        return
    raise AssertionError("重复 key 应抛 ValueError")


def test_missing_key():
    _reset()

    try:
        class Broken(solution.Plugin):
            pass
    except TypeError:
        return
    raise AssertionError("缺少 key 应抛 TypeError")


def test_metaclass_type():
    _reset()

    class A(solution.Plugin):
        key = "a"

    assert type(A) is solution.PluginMeta


def test_base_not_registered():
    _reset()
    assert solution.PluginMeta.registry == {}, "根基类本身不应进入注册表"


run([
    ("子类自动注册", test_registers_subclass),
    ("注册多个子类", test_registers_multiple),
    ("重复 key 报错", test_duplicate_key),
    ("缺少 key 报错", test_missing_key),
    ("元类类型正确", test_metaclass_type),
    ("根基类不注册", test_base_not_registered),
])
