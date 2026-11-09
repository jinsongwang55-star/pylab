"""1.7 综合练习：带 JSON 持久化的记账核心。

要求见右侧课程正文，完成后点「检查」。
"""

import json
import os
from decimal import Decimal
from pathlib import Path


class Ledger:
    def __init__(self, path):
        self.path = Path(path)
        self.records = []
        # TODO: 文件存在时读取并解析到 self.records

    def add(self, amount, desc, tag="其他"):
        raise NotImplementedError("删掉这一行，开始实现")

    def list(self, tag=None):
        raise NotImplementedError("删掉这一行，开始实现")

    def total(self):
        raise NotImplementedError("删掉这一行，开始实现")
