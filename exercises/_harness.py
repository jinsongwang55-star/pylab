"""练习测试的最小运行器（不依赖 pytest）。

每个 tests.py 用 run([(名称, 函数), ...]) 注册用例，
结果以带标记的单行 JSON 打印，由 server.py 解析。
"""

import json

SENTINEL = "__PYLAB_RESULTS__"


def run(cases):
    results = []
    for name, case in cases:
        try:
            case()
            results.append({"name": name, "ok": True, "msg": ""})
        except AssertionError as exc:
            results.append({"name": name, "ok": False, "msg": str(exc) or "断言失败"})
        except Exception as exc:  # noqa: BLE001 - 学员代码可能抛出任意异常
            results.append({"name": name, "ok": False, "msg": f"{type(exc).__name__}: {exc}"})
    print(SENTINEL + json.dumps(results, ensure_ascii=False))
