#!/usr/bin/env python3
"""本机自检：走真实启动链路，验证启动、接口、停止是否正常。

Windows 上会调用 launch.vbs（与桌面快捷方式同一条链路），
Linux / macOS 上调用 launch.sh。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PID_FILE = DATA / "server.pid"
PORT_FILE = DATA / "server.port"
LOG_FILE = DATA / "server.log"

results: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def read_port() -> int | None:
    try:
        return int(PORT_FILE.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def run_launcher() -> int:
    if os.name == "nt":
        wscript = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "wscript.exe"
        return subprocess.run(
            [str(wscript), str(ROOT / "launch.vbs")], cwd=ROOT, check=False
        ).returncode
    return subprocess.run(["bash", str(ROOT / "launch.sh")], cwd=ROOT, check=False).returncode


def run_stop() -> int:
    return subprocess.run(
        [sys.executable, str(ROOT / "stop.py")], cwd=ROOT, check=False
    ).returncode


def wait_ready(timeout: float = 20.0) -> tuple[int | None, int | None]:
    deadline = time.time() + timeout
    while time.time() < deadline:
        port = read_port()
        if port:
            try:
                url = f"http://127.0.0.1:{port}/api/curriculum"
                with urllib.request.urlopen(url, timeout=2) as response:
                    payload = json.loads(response.read())
                return port, int(payload.get("total", 0))
            except Exception:  # noqa: BLE001 - 服务可能还没就绪
                pass
        time.sleep(0.2)
    return None, None


def main() -> int:
    print(f"平台: {sys.platform} | Python {sys.version.split()[0]}")
    print(f"项目: {ROOT}\n")

    ok = sys.version_info >= (3, 10)
    record("Python 版本 >= 3.10", ok, sys.version.split()[0])

    required = ["server.py", "launcher.py", "stop.py", "curriculum.json", "static/index.html"]
    missing = [name for name in required if not (ROOT / name).exists()]
    record("核心文件存在", not missing, "缺失: " + ", ".join(missing) if missing else "")

    run_stop()
    for path in (PID_FILE, PORT_FILE):
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        except OSError:
            pass

    code = run_launcher()
    record("启动器退出码为 0", code == 0, f"exit={code}")

    port, total = wait_ready()
    record("服务可访问", port is not None, f"端口 {port}" if port else "20 秒内未就绪")
    record("课程接口有数据", bool(total), f"{total} 节" if total else "返回为空")

    stop_code = run_stop()
    record("停止器退出码为 0", stop_code == 0, f"exit={stop_code}")
    record("状态文件已清理", not PID_FILE.exists() and not PORT_FILE.exists())

    failures = [name for name, passed, _ in results if not passed]
    print("\n" + "=" * 50)
    if failures:
        print(f"自检失败: {len(failures)} 项 — " + ", ".join(failures))
        if LOG_FILE.exists():
            print("\n--- data/server.log 末尾 ---")
            lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
            print("\n".join(lines[-15:]))
        return 1

    print("自检全部通过，双击启动链路正常。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
