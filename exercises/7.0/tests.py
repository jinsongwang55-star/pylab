import solution
from _harness import run


def _product_class():
    class Product:
        price = solution.Positive()
        stock = solution.Positive()

    return Product


def test_class_access_returns_descriptor():
    Product = _product_class()
    assert isinstance(Product.price, solution.Positive), "通过类访问应返回描述符自身"


def test_set_and_get():
    Product = _product_class()
    item = Product()
    item.price = 9.9
    assert item.price == 9.9


def test_instances_independent():
    Product = _product_class()
    first, second = Product(), Product()
    first.price = 10
    second.price = 20
    assert first.price == 10
    assert second.price == 20


def test_reject_non_number():
    Product = _product_class()
    item = Product()
    for value in ("10", None, True):
        try:
            item.price = value
        except ValueError:
            continue
        raise AssertionError(f"{value!r} 应抛 ValueError")


def test_reject_non_positive():
    Product = _product_class()
    item = Product()
    for value in (0, -1, -0.5):
        try:
            item.price = value
        except ValueError:
            continue
        raise AssertionError(f"{value!r} 应抛 ValueError")


def test_unset_attribute_message():
    Product = _product_class()
    item = Product()
    try:
        item.price
    except AttributeError as exc:
        assert "price" in str(exc), f"错误消息应包含属性名: {exc}"
        return
    raise AssertionError("未赋值时应抛 AttributeError")


run([
    ("类访问返回描述符", test_class_access_returns_descriptor),
    ("实例存取", test_set_and_get),
    ("实例之间互不影响", test_instances_independent),
    ("拒绝非数字", test_reject_non_number),
    ("拒绝非正数", test_reject_non_positive),
    ("未赋值错误信息", test_unset_attribute_message),
])
