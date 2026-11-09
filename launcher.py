#!/usr/bin/env python3
"""PyLab 跨平台启动器：检查已有实例、后台启动服务、打开浏览器。

Linux / macOS 由 launch.sh 调用，Windows 由 launch.bat 调用。
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import webbrowser
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PID_FILE = DATA / "server.pid"
PORT_FILE = DATA / "server.port"
LOG_FILE = DATA / "server.log"

START_TIMEOUT = 10.0

if sys.version_info < (3, 10):
    print("需要 Python 3.10 或更高版本。")
    raise SystemExit(1)


def log(message: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    try:
        print(line)
    except OSError:
        pass
    try:
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


def read_int(path: Path) -> int | None:
    try:
        return int(path.read_text(encoding="utf-8").strip())
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


def open_browser(url: str) -> None:
    try:
        webbrowser.open(url)
    except Exception:  # noqa: BLE001 - 无图形环境下打开失败不影响启动
        pass


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)

    existing = read_int(PID_FILE)
    if existing and pid_alive(existing):
        port = read_int(PORT_FILE) or 8000
        url = f"http://127.0.0.1:{port}/"
        log(f"已在运行（PID {existing}），打开 {url}")
        open_browser(url)
        return 0

    for path in (PID_FILE, PORT_FILE):
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        except OSError:
            pass

    log("PyLab 启动")

    with LOG_FILE.open("a", encoding="utf-8", buffering=1) as log_file:
        kwargs = {
            "cwd": ROOT,
            "stdin": subprocess.DEVNULL,
            "stdout": log_file,
            "stderr": log_file,
        }
        if os.name == "nt":
            kwargs["creationflags"] = (
                subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
            )
        else:
            kwargs["start_new_session"] = True
        process = subprocess.Popen([sys.executable, "server.py", "--no-open"], **kwargs)

        deadline = time.time() + START_TIMEOUT
        port = None
        while time.time() < deadline:
            if process.poll() is not None:
                break
            port = read_int(PORT_FILE)
            if port:
                break
            time.sleep(0.1)

    if not port:
        log("启动失败，详见 data/server.log")
        return 1

    url = f"http://127.0.0.1:{port}/"
    log(f"已启动: {url}")
    open_browser(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
