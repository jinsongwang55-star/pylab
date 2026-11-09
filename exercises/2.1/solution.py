"""2.1 参考答案：日志行解析与手机号脱敏。"""

import re

LOG_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) \[([A-Z]+)\] (.+)$")
PHONE_PATTERN = re.compile(r"(?<!\d)(1\d{2})\d{4}(\d{4})(?!\d)")


def parse_log_line(line: str) -> dict[str, str] | None:
    match = LOG_PATTERN.match(line)
    if match is None:
        return None
    return {
        "date": match.group(1),
        "time": match.group(2),
        "level": match.group(3),
        "message": match.group(4),
    }


def mask_phones(text: str) -> str:
    return PHONE_PATTERN.sub(r"\1****\2", text)
