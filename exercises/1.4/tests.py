import io
from contextlib import redirect_stdout

import solution
from _harness import run


def _capture(function, *args, **kwargs):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = function(*args, **kwargs)
    return result, buffer.getvalue()


def test_output_format():
    @solution.log_calls
    def add(a, b):
        return a + b

    _, output = _capture(add, 1, 2)
    assert output == "[call] add\n", f"输出格式不对，实际是 {output!r}"


def test_return_value():
    @solution.log_calls
    def multiply(a, b):
        return a * b

    result, _ = _capture(multiply, 3, 4)
    assert result == 12, f"应返回原函数结果 12，实际是 {result!r}"


def test_preserves_name():
    @solution.log_calls
    def hello():
        return "hi"

    assert hello.__name__ == "hello", "必须用 functools.wraps 保留 __name__"


def test_preserves_doc():
    @solution.log_calls
    def hello():
        """打个招呼"""
        return "hi"

    assert hello.__doc__ == "打个招呼", "必须保留原函数的 __doc__"


def test_passes_kwargs():
    @solution.log_calls
    def join(*parts, sep="-"):
        return sep.join(parts)

    result, _ = _capture(join, "a", "b", sep="+")
    assert result == "a+b", f"关键字参数应原样传给原函数，实际 {result!r}"


run([
    ("打印格式为 [call] 函数名", test_output_format),
    ("返回原函数结果", test_return_value),
    ("保留 __name__", test_preserves_name),
    ("保留 __doc__", test_preserves_doc),
    ("正确透传关键字参数", test_passes_kwargs),
])
