"""5.1 参考答案：在入口校验用户数据。"""

import re

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]+$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_user(payload):
    errors = []
    cleaned = {}

    username = payload.get("username")
    if not isinstance(username, str):
        errors.append({"field": "username", "message": "必须是字符串"})
    else:
        username = username.strip()
        if not 3 <= len(username) <= 20:
            errors.append({"field": "username", "message": "长度必须在 3-20 之间"})
        elif not USERNAME_RE.match(username):
            errors.append({"field": "username", "message": "只允许字母、数字和下划线"})
        else:
            cleaned["username"] = username

    email = payload.get("email")
    if not isinstance(email, str):
        errors.append({"field": "email", "message": "必须是字符串"})
    else:
        email = email.strip()
        if not EMAIL_RE.match(email):
            errors.append({"field": "email", "message": "邮箱格式不正确"})
        else:
            cleaned["email"] = email

    age = payload.get("age")
    if isinstance(age, bool) or not isinstance(age, int):
        errors.append({"field": "age", "message": "必须是整数"})
    elif not 0 <= age <= 150:
        errors.append({"field": "age", "message": "必须在 0-150 之间"})
    else:
        cleaned["age"] = age

    if errors:
        return None, errors
    return cleaned, []
