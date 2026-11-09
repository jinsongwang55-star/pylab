#!/usr/bin/env python3
"""PyLab 跨平台停止器：按 data/server.pid 终止服务并清理状态文件。"""

from __future__ import annotations

import os
import signal
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PID_FILE = DATA / "server.pid"
PORT_FILE = DATA / "server.port"


def read_pid() -> int | None:
    try:
        return int(PID_FILE.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes

        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def terminate(pid: int, force: bool = False) -> None:
    if os.name == "nt":
        args = ["taskkill", "/PID", str(pid), "/F"]
        subprocess.run(args, capture_output=True, check=False)
        return
    os.kill(pid, signal.SIGKILL if force else signal.SIGTERM)


def cleanup() -> None:
    for path in (PID_FILE, PORT_FILE):
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        except OSError:
            pass


def main() -> int:
    pid = read_pid()
    if pid is None:
        print("PyLab 没有在运行。")
        cleanup()
        return 0

    if not pid_alive(pid):
        print("进程已不存在，清理残留状态文件。")
        cleanup()
        return 0

    terminate(pid)
    for _ in range(30):
        if not pid_alive(pid):
            break
        time.sleep(0.1)
    if pid_alive(pid):
        terminate(pid, force=True)
        time.sleep(0.3)

    cleanup()
    if pid_alive(pid):
        print(f"停止失败，请手动结束 PID {pid}。")
        return 1
    print(f"已停止 PyLab（PID {pid}）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
