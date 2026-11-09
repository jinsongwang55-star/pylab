"""1.6 参考答案：atomic_json 上下文管理器。"""

import copy
import json
import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def atomic_json(path, default):
    path = Path(path)
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = copy.deepcopy(default)
    yield data
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)
