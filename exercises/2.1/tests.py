import solution
from _harness import run


def test_parse_normal():
    got = solution.parse_log_line("2026-11-09 10:23:41 [ERROR] 数据库连接失败")
    expected = {
        "date": "2026-11-09",
        "time": "10:23:41",
        "level": "ERROR",
        "message": "数据库连接失败",
    }
    assert got == expected, f"解析结果不对: {got}"


def test_message_with_brackets():
    got = solution.parse_log_line("2026-11-09 10:23:41 [INFO] 用户 [admin] 登录")
    assert got is not None, "这行应当匹配"
    assert got["message"] == "用户 [admin] 登录", f"message 被截断: {got['message']!r}"


def test_invalid_lines():
    samples = [
        "",
        "hello",
        "2026-11-09 [INFO] 缺时间",
        "2026-11-09 10:23:41 INFO 缺方括号",
        "2026-11-09 10:23:41 [INFO] 多出尾部\n第二行",
    ]
    for line in samples:
        assert solution.parse_log_line(line) is None, f"{line!r} 应返回 None"


def test_mask_basic():
    assert solution.mask_phones("电话 13812348000") == "电话 138****8000"


def test_mask_multiple():
    text = "A 13812348000 B 13900001111"
    assert solution.mask_phones(text) == "A 138****8000 B 139****1111"


def test_mask_boundaries():
    assert solution.mask_phones("138123480001") == "138123480001", "12 位数字不应被处理"
    assert solution.mask_phones("1381234800") == "1381234800", "10 位数字不应被处理"
    assert solution.mask_phones("订单号 913812348000") == "订单号 913812348000", "长数字串不应被截取"


run([
    ("解析标准日志行", test_parse_normal),
    ("message 可含方括号", test_message_with_brackets),
    ("非法行返回 None", test_invalid_lines),
    ("单手机号脱敏", test_mask_basic),
    ("多手机号脱敏", test_mask_multiple),
    ("数字边界不误伤", test_mask_boundaries),
])
