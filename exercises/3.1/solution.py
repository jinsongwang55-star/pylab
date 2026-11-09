"""3.1 参考答案：用冻结 dataclass 表达不可变数据。"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Item:
    name: str
    price: Decimal
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name 不能为空")
        if self.price <= 0:
            raise ValueError("price 必须大于 0")
