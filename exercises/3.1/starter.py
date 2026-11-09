"""3.1 练习：用冻结 dataclass 表达不可变数据。"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Item:
    name: str
    price: Decimal
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        # TODO: name.strip() 为空抛 ValueError；price <= 0 抛 ValueError
        pass
