import gc

import solution
from _harness import run


class Box:
    pass


def test_point_basic():
    point = solution.Point(1, 2)
    assert point.x == 1 and point.y == 2


def test_point_has_no_dict():
    point = solution.Point(1, 2)
    assert not hasattr(point, "__dict__"), "__slots__ 类不应有 __dict__"


def test_point_rejects_new_attribute():
    point = solution.Point(1, 2)
    try:
        point.z = 3
    except AttributeError:
        return
    raise AssertionError("声明 __slots__ 后新增属性应抛 AttributeError")


def test_cache_roundtrip():
    cache = solution.WeakCache()
    box = Box()
    cache.put("a", box)
    assert cache.get("a") is box
    assert cache.get("missing", "fallback") == "fallback"


def test_cache_drops_on_gc():
    cache = solution.WeakCache()
    box = Box()
    cache.put("a", box)
    del box
    gc.collect()
    assert len(cache) == 0, "对象只剩弱引用后，缓存应自动移除"
    assert cache.get("a") is None


def test_cache_overwrite_and_len():
    cache = solution.WeakCache()
    first, second = Box(), Box()
    cache.put("k", first)
    cache.put("k", second)
    assert len(cache) == 1
    assert cache.get("k") is second


run([
    ("Point 正常存取", test_point_basic),
    ("Point 没有 __dict__", test_point_has_no_dict),
    ("Point 拒绝新属性", test_point_rejects_new_attribute),
    ("缓存存取", test_cache_roundtrip),
    ("对象回收后缓存自动清理", test_cache_drops_on_gc),
    ("覆盖写入与长度", test_cache_overwrite_and_len),
])
