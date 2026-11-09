import solution
from _harness import run


def build():
    router = solution.Router()
    router.add("GET", "/posts", lambda: {"items": []})
    router.add("GET", "/posts/{post_id}", lambda post_id: {"id": post_id})
    router.add("POST", "/posts", lambda: {"created": True})
    router.add(
        "GET",
        "/users/{user_id}/posts/{post_id}",
        lambda user_id, post_id: {"user": user_id, "post": post_id},
    )
    return router


def test_static_route():
    status, body = build().dispatch("GET", "/posts")
    assert (status, body) == (200, {"items": []})


def test_single_param():
    status, body = build().dispatch("GET", "/posts/42")
    assert status == 200
    assert body == {"id": "42"}, f"路径参数应作为字符串传入: {body}"


def test_multi_param():
    status, body = build().dispatch("GET", "/users/7/posts/9")
    assert status == 200
    assert body == {"user": "7", "post": "9"}


def test_method_not_allowed():
    status, body = build().dispatch("DELETE", "/posts")
    assert status == 405
    assert body["error"] == "Method Not Allowed"


def test_not_found():
    status, body = build().dispatch("GET", "/nope")
    assert status == 404
    assert body["error"] == "Not Found"


def test_no_prefix_match():
    status, _ = build().dispatch("GET", "/posts/42/extra")
    assert status == 404, "段数不一致时不应匹配"


def test_handler_result_preserved():
    router = solution.Router()
    router.add("POST", "/echo", lambda: {"ok": True, "count": 3})
    status, body = router.dispatch("POST", "/echo")
    assert status == 200
    assert body == {"ok": True, "count": 3}


run([
    ("静态路由匹配", test_static_route),
    ("单路径参数", test_single_param),
    ("多路径参数", test_multi_param),
    ("路径存在但方法不符", test_method_not_allowed),
    ("路径不存在", test_not_found),
    ("不做前缀匹配", test_no_prefix_match),
    ("保留 handler 返回值", test_handler_result_preserved),
])
