"""1.6 练习：实现 atomic_json 上下文管理器。

要求见右侧课程正文，完成后点「检查」。
"""

from contextlib import contextmanager


@contextmanager
def atomic_json(path, default):
    """成功退出时原子写回 JSON；块内抛异常时不写盘。"""
    raise NotImplementedError("删掉这一行，开始实现")
