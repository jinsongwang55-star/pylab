"""1.4 参考答案：log_calls 装饰器。"""

from functools import wraps


def log_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[call] {func.__name__}")
        return func(*args, **kwargs)

    return wrapper
