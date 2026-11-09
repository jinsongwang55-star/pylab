import solution
from _harness import run

SALT = bytes(range(16))


def test_hash_format():
    stored = solution.hash_password("secret", salt=SALT)
    parts = stored.split("$")
    assert len(parts) == 4, f"格式应为四段: {stored!r}"
    assert parts[0] == "pbkdf2_sha256"
    assert int(parts[1]) >= 100_000, "迭代次数不应低于 10 万"
    assert parts[2] == SALT.hex(), "salt 应原样写入"
    assert len(parts[3]) == 64, "sha256 十六进制长度应为 64"


def test_verify_correct_password():
    stored = solution.hash_password("secret", salt=SALT)
    assert solution.verify_password("secret", stored) is True


def test_verify_wrong_password():
    stored = solution.hash_password("secret", salt=SALT)
    assert solution.verify_password("wrong", stored) is False
    assert solution.verify_password("secret", "not-a-hash") is False


def test_token_roundtrip():
    token = solution.make_token(7, "s3cret", ttl=60, now=1000)
    assert solution.verify_token(token, "s3cret", now=1000) == 7
    assert solution.verify_token(token, "s3cret", now=1059) == 7


def test_token_expiry_boundary():
    token = solution.make_token(7, "s3cret", ttl=60, now=1000)
    assert solution.verify_token(token, "s3cret", now=1060) is None, "now == expires 应视为过期"


def test_token_invalid():
    token = solution.make_token(7, "s3cret", ttl=60, now=1000)
    _, expires, signature = token.split(".")
    assert solution.verify_token(f"8.{expires}.{signature}", "s3cret", now=1000) is None, "篡改 user_id 应失效"
    assert solution.verify_token(token, "other-secret", now=1000) is None, "错误密钥应失效"
    assert solution.verify_token("garbage", "s3cret", now=1000) is None


run([
    ("哈希格式与参数", test_hash_format),
    ("正确密码验证通过", test_verify_correct_password),
    ("错误密码与非法格式", test_verify_wrong_password),
    ("令牌往返", test_token_roundtrip),
    ("过期边界", test_token_expiry_boundary),
    ("篡改与错误密钥", test_token_invalid),
])
