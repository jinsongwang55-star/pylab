"""2.1 练习：日志行解析与手机号脱敏。"""


def parse_log_line(line: str) -> dict[str, str] | None:
    """解析 'YYYY-MM-DD HH:MM:SS [LEVEL] message'，不匹配返回 None。"""
    raise NotImplementedError("删掉这一行，开始实现")


def mask_phones(text: str) -> str:
    """把 11 位手机号中间四位替换为 ****，前后不能是数字。"""
    raise NotImplementedError("删掉这一行，开始实现")
