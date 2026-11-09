import solution
from _harness import run


def define_user():
    class User(solution.Model):
        name = solution.Field(str)
        age = solution.Field(int)
        nickname = solution.Field(str, default="匿名")

    return User


def test_fields_collected():
    User = define_user()
    assert list(User._fields) == ["name", "age", "nickname"], f"字段顺序不对: {list(User._fields)}"


def test_class_access_returns_field():
    User = define_user()
    assert isinstance(User.name, solution.Field), "通过类访问应返回 Field 对象"


def test_init_and_defaults():
    User = define_user()
    user = User(name="alice", age=30)
    assert user.name == "alice"
    assert user.age == 30
    assert user.nickname == "匿名"


def test_type_validation():
    User = define_user()
    try:
        User(name="alice", age="30")
    except TypeError:
        return
    raise AssertionError("age 传入字符串应抛 TypeError")


def test_bool_rejected_for_int():
    User = define_user()
    try:
        User(name="alice", age=True)
    except TypeError:
        return
    raise AssertionError("bool 不应被当作 int 接受")


def test_unknown_field():
    User = define_user()
    try:
        User(name="alice", age=30, email="x@example.com")
    except TypeError:
        return
    raise AssertionError("未知字段应抛 TypeError")


def test_to_dict():
    User = define_user()
    user = User(name="alice", age=30)
    assert user.to_dict() == {"name": "alice", "age": 30, "nickname": "匿名"}


def test_from_dict():
    User = define_user()
    user = User.from_dict({"name": "bob", "age": 20})
    assert isinstance(user, User)
    assert user.name == "bob"
    assert user.age == 20


def test_instances_independent():
    User = define_user()
    first = User(name="a", age=1)
    second = User(name="b", age=2)
    assert first.name == "a"
    assert second.name == "b"


run([
    ("字段按顺序收集", test_fields_collected),
    ("类访问返回 Field", test_class_access_returns_field),
    ("初始化与默认值", test_init_and_defaults),
    ("类型校验", test_type_validation),
    ("int 字段拒绝 bool", test_bool_rejected_for_int),
    ("未知字段报错", test_unknown_field),
    ("to_dict 顺序稳定", test_to_dict),
    ("from_dict 构造实例", test_from_dict),
    ("实例之间互不影响", test_instances_independent),
])
