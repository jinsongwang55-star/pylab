import solution
from _harness import run

VALID = {"username": "alice_01", "email": "alice@example.com", "age": 30}


def _fields(errors):
    return {item["field"] for item in errors}


def test_valid_payload():
    cleaned, errors = solution.validate_user(dict(VALID))
    assert errors == [], f"不应有错误: {errors}"
    assert cleaned == VALID


def test_missing_all_fields():
    cleaned, errors = solution.validate_user({})
    assert cleaned is None
    assert _fields(errors) == {"username", "email", "age"}, f"应一次返回三个字段错误: {errors}"
    assert all(item["message"] for item in errors), "每条错误都要有说明"


def test_username_rules():
    for name in ("ab", "a" * 21, "bad name", "bad-name"):
        cleaned, errors = solution.validate_user({**VALID, "username": name})
        assert cleaned is None, f"{name!r} 应被判非法"
        assert "username" in _fields(errors)


def test_email_rules():
    for email in ("alice", "alice@", "alice@example", "@example.com", "a b@example.com"):
        cleaned, errors = solution.validate_user({**VALID, "email": email})
        assert cleaned is None, f"{email!r} 应被判非法"
        assert "email" in _fields(errors)


def test_age_rules():
    for age in (-1, 151, "30", True, 3.5):
        cleaned, errors = solution.validate_user({**VALID, "age": age})
        assert cleaned is None, f"age={age!r} 应被判非法"
        assert "age" in _fields(errors)


def test_extra_fields_dropped():
    cleaned, errors = solution.validate_user({**VALID, "is_admin": True, "id": 1})
    assert errors == []
    assert cleaned == VALID, f"无关字段应被丢弃: {cleaned}"


def test_whitespace_stripped():
    cleaned, errors = solution.validate_user(
        {"username": "  alice_01  ", "email": "  alice@example.com  ", "age": 30}
    )
    assert errors == []
    assert cleaned == VALID


run([
    ("合法数据通过", test_valid_payload),
    ("缺失字段一次性返回", test_missing_all_fields),
    ("用户名校验", test_username_rules),
    ("邮箱校验", test_email_rules),
    ("年龄校验", test_age_rules),
    ("丢弃无关字段", test_extra_fields_dropped),
    ("去除首尾空格", test_whitespace_stripped),
])
