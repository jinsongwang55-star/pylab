"""5.4 综合练习：用路由、校验、鉴权拼一个迷你 API。

起始代码提供可直接使用的密码哈希与令牌工具；你只需要实现 handle_request。
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time

ITERATIONS = 120_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
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


def make_token(user_id: int, secret: str, ttl: int = 3600) -> str:
    payload = f"{user_id}.{int(time.time()) + ttl}"
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def verify_token(token: str, secret: str) -> int | None:
    try:
        user_id, expires, signature = token.split(".")
        expected = hmac.new(
            secret.encode(), f"{user_id}.{expires}".encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        if int(time.time()) >= int(expires):
            return None
        return int(user_id)
    except (ValueError, AttributeError):
        return None


def handle_request(method, path, body, *, secret, db, headers=None):
    """实现四个端点，返回 (status_code, payload)。"""
    raise NotImplementedError("删掉这一行，开始实现")
