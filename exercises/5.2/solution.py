"""5.2 参考答案：密码哈希与签名令牌。"""

import hashlib
import hmac
import os
import time

ITERATIONS = 260_000


def hash_password(password, *, salt=None):
    salt = os.urandom(16) if salt is None else salt
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password, stored):
    try:
        algorithm, iterations, salt_hex, hash_hex = stored.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(digest.hex(), hash_hex)


def make_token(user_id, secret, ttl=3600, now=None):
    current = int(time.time()) if now is None else now
    payload = f"{user_id}.{current + ttl}"
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def verify_token(token, secret, now=None):
    try:
        user_id, expires, signature = token.split(".")
        expected = hmac.new(
            secret.encode(), f"{user_id}.{expires}".encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        current = int(time.time()) if now is None else now
        if current >= int(expires):
            return None
        return int(user_id)
    except (ValueError, AttributeError):
        return None
