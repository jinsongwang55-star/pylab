"""1.7 参考答案：带 JSON 持久化的记账核心。"""

import json
import os
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path


class Ledger:
    def __init__(self, path):
        self.path = Path(path)
        if self.path.exists():
            self.records = json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self.records = []

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(self.records, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, self.path)

    def add(self, amount, desc, tag="其他"):
        try:
            value = Decimal(str(amount))
        except (InvalidOperation, ValueError):
            raise ValueError(f"非法金额: {amount!r}") from None
        if not value.is_finite() or value <= 0:
            raise ValueError("金额必须是正数")
        record = {
            "id": max((int(r["id"]) for r in self.records), default=0) + 1,
            "amount": str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "desc": desc,
            "tag": tag,
        }
        self.records.append(record)
        self._save()
        return dict(record)

    def list(self, tag=None):
        return [dict(r) for r in self.records if tag is None or r["tag"] == tag]

    def total(self):
        return sum((Decimal(r["amount"]) for r in self.records), Decimal("0"))
