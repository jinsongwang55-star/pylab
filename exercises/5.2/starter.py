"""5.2 练习：密码哈希与签名令牌。"""


def hash_password(password, *, salt=None):
    """返回 pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>。"""
    raise NotImplementedError("删掉这一行，开始实现")


def verify_password(password, stored):
    """密码正确返回 True；格式非法或密码错误返回 False。"""
    raise NotImplementedError("删掉这一行，开始实现")


def make_token(user_id, secret, ttl=3600, now=None):
    """返回 <user_id>.<expires_at>.<signature>。"""
    raise NotImplementedError("删掉这一行，开始实现")


def verify_token(token, secret, now=None):
    """有效返回 user_id，否则返回 None。"""
    raise NotImplementedError("删掉这一行，开始实现")
