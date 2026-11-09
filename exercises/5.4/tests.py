import solution
from _harness import run

SECRET = "test-secret"


def _db():
    return {"users": [], "posts": []}


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _register(db, username="alice", password="secret1"):
    return solution.handle_request(
        "POST", "/users", {"username": username, "password": password}, secret=SECRET, db=db
    )


def _login(db, username="alice", password="secret1"):
    return solution.handle_request(
        "POST", "/login", {"username": username, "password": password}, secret=SECRET, db=db
    )


def test_register_success():
    db = _db()
    status, payload = _register(db)
    assert status == 201, f"应返回 201，实际 {status}"
    assert payload["username"] == "alice"
    assert payload["id"] == 1
    assert "password" not in payload and "password_hash" not in payload, "不能回传密码"
    assert len(db["users"]) == 1


def test_register_duplicate():
    db = _db()
    _register(db)
    status, payload = _register(db, password="other12")
    assert status == 409, f"重复用户名应返回 409，实际 {status}"
    assert payload["error"]


def test_register_invalid():
    db = _db()
    for body in (
        {"username": "ab", "password": "secret1"},
        {"username": "alice", "password": "123"},
        {"username": "", "password": "secret1"},
    ):
        status, _ = solution.handle_request("POST", "/users", body, secret=SECRET, db=db)
        assert status == 400, f"{body} 应返回 400，实际 {status}"
    assert db["users"] == [], "非法注册不应写入数据"


def test_login_success():
    db = _db()
    _register(db)
    status, payload = _login(db)
    assert status == 200
    assert solution.verify_token(payload["token"], SECRET) == 1


def test_login_failure():
    db = _db()
    _register(db)
    for body in (
        {"username": "alice", "password": "wrong12"},
        {"username": "nobody", "password": "secret1"},
    ):
        status, _ = solution.handle_request("POST", "/login", body, secret=SECRET, db=db)
        assert status == 401, f"{body} 应返回 401，实际 {status}"


def test_create_post_requires_token():
    db = _db()
    status, _ = solution.handle_request(
        "POST", "/posts", {"title": "t", "content": "c"}, secret=SECRET, db=db
    )
    assert status == 401, "缺少 token 应返回 401"

    status, _ = solution.handle_request(
        "POST", "/posts", {"title": "t", "content": "c"}, secret=SECRET, db=db,
        headers={"Authorization": "Bearer broken"},
    )
    assert status == 401, "无效 token 应返回 401"
    assert db["posts"] == []


def test_create_and_list_posts():
    db = _db()
    _register(db)
    _, login = _login(db)
    token = login["token"]

    status, first = solution.handle_request(
        "POST", "/posts", {"title": "第一篇", "content": "A"}, secret=SECRET, db=db,
        headers=_auth(token),
    )
    assert status == 201
    assert first["author_id"] == 1

    status, _ = solution.handle_request(
        "POST", "/posts", {"title": "", "content": "B"}, secret=SECRET, db=db,
        headers=_auth(token),
    )
    assert status == 400, "空标题应返回 400"

    status, _ = solution.handle_request(
        "POST", "/posts", {"title": "第二篇", "content": "B"}, secret=SECRET, db=db,
        headers=_auth(token),
    )
    assert status == 201

    status, listing = solution.handle_request("GET", "/posts", None, secret=SECRET, db=db)
    assert status == 200
    titles = [item["title"] for item in listing["items"]]
    assert titles == ["第二篇", "第一篇"], f"应按新到旧返回，实际 {titles}"


def test_not_found_and_method_not_allowed():
    db = _db()
    status, _ = solution.handle_request("GET", "/nope", None, secret=SECRET, db=db)
    assert status == 404

    status, _ = solution.handle_request("PUT", "/posts", {}, secret=SECRET, db=db)
    assert status == 405


run([
    ("注册成功", test_register_success),
    ("重复用户名", test_register_duplicate),
    ("非法注册被拒绝", test_register_invalid),
    ("登录成功拿到可用令牌", test_login_success),
    ("登录失败统一 401", test_login_failure),
    ("发文必须带有效令牌", test_create_post_requires_token),
    ("发文与列表顺序", test_create_and_list_posts),
    ("404 与 405", test_not_found_and_method_not_allowed),
])
