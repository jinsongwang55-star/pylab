"""5.4 参考答案：用路由、校验、鉴权拼一个迷你 API。"""

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
    method = method.upper()
    headers = headers or {}

    if path == "/users":
        if method != "POST":
            return 405, {"error": "Method Not Allowed"}
        data = body or {}
        username = data.get("username")
        password = data.get("password")
        if not isinstance(username, str) or not 3 <= len(username.strip()) <= 20:
            return 400, {"error": "用户名长度必须为 3-20"}
        if not isinstance(password, str) or len(password) < 6:
            return 400, {"error": "密码至少 6 位"}
        username = username.strip()
        if any(user["username"] == username for user in db["users"]):
            return 409, {"error": "用户名已存在"}
        user = {
            "id": len(db["users"]) + 1,
            "username": username,
            "password_hash": hash_password(password),
        }
        db["users"].append(user)
        return 201, {"id": user["id"], "username": user["username"]}

    if path == "/login":
        if method != "POST":
            return 405, {"error": "Method Not Allowed"}
        data = body or {}
        username = data.get("username")
        password = data.get("password")
        user = next((item for item in db["users"] if item["username"] == username), None)
        if (
            user is None
            or not isinstance(password, str)
            or not verify_password(password, user["password_hash"])
        ):
            return 401, {"error": "用户名或密码错误"}
        return 200, {"token": make_token(user["id"], secret)}

    if path == "/posts":
        if method == "GET":
            return 200, {"items": [dict(post) for post in reversed(db["posts"])]}

        if method == "POST":
            header = headers.get("Authorization") or headers.get("authorization") or ""
            token = header[len("Bearer "):].strip() if header.startswith("Bearer ") else ""
            user_id = verify_token(token, secret) if token else None
            if user_id is None:
                return 401, {"error": "未登录或令牌无效"}

            data = body or {}
            title = data.get("title")
            content = data.get("content")
            if not isinstance(title, str) or not title.strip():
                return 400, {"error": "标题不能为空"}
            if not isinstance(content, str) or not content.strip():
                return 400, {"error": "内容不能为空"}

            post = {
                "id": len(db["posts"]) + 1,
                "author_id": user_id,
                "title": title.strip(),
                "content": content.strip(),
            }
            db["posts"].append(post)
            return 201, dict(post)

        return 405, {"error": "Method Not Allowed"}

    return 404, {"error": "Not Found"}
