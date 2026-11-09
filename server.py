#!/usr/bin/env python3
"""PyLab —— 本地 Python 学习与验证平台（纯标准库，无第三方依赖）。

启动:
    python server.py                 # 默认 http://127.0.0.1:8000
    python server.py --port 8100     # 指定端口（被占用时自动向后顺延）
    python server.py --no-open       # 不自动打开浏览器

安全说明:
    服务只绑定 127.0.0.1，且会执行你在编辑器里写的代码。
    这是学习工具的固有设计，不要把它暴露到公网。
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import markdown_render

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
CONTENT_DIR = ROOT / "content"
EXERCISE_DIR = ROOT / "exercises"
PROGRESS_FILE = ROOT / "data" / "progress.json"
PID_FILE = ROOT / "data" / "server.pid"
PORT_FILE = ROOT / "data" / "server.port"
CURRICULUM_FILE = ROOT / "curriculum.json"

RUN_TIMEOUT = 5.0
CHECK_TIMEOUT = 10.0
MAX_OUTPUT = 20_000
SENTINEL = "__PYLAB_RESULTS__"

PROGRESS_LOCK = threading.Lock()


# ---------------------------------------------------------------------------
# 数据读取
# ---------------------------------------------------------------------------
def _load_curriculum() -> dict:
    return json.loads(CURRICULUM_FILE.read_text(encoding="utf-8"))


def _load_progress() -> dict:
    if not PROGRESS_FILE.exists():
        return {}
    try:
        payload = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        return {}


def _save_progress(progress: dict) -> None:
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = PROGRESS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, PROGRESS_FILE)


def _find_lesson(lesson_id: str) -> tuple[dict | None, dict | None]:
    for stage in _load_curriculum()["stages"]:
        for lesson in stage.get("lessons", []):
            if lesson["id"] == lesson_id:
                return stage, lesson
    return None, None


def _curriculum_payload() -> dict:
    curriculum = _load_curriculum()
    progress = _load_progress()
    total = done = 0
    for stage in curriculum["stages"]:
        for lesson in stage.get("lessons", []):
            total += 1
            status = progress.get(lesson["id"], {}).get("status", "todo")
            lesson["status"] = status
            if status == "done":
                done += 1
    curriculum["total"] = total
    curriculum["done"] = done
    return curriculum


def _lesson_payload(lesson_id: str) -> dict | None:
    stage, lesson = _find_lesson(lesson_id)
    if lesson is None:
        return None
    html = markdown_render.render((CONTENT_DIR / lesson["file"]).read_text(encoding="utf-8"))
    payload = {
        "id": lesson["id"],
        "title": lesson["title"],
        "type": lesson["type"],
        "stage": stage["title"],
        "minutes": lesson.get("minutes", 20),
        "html": html,
        "status": _load_progress().get(lesson["id"], {}).get("status", "todo"),
        "exercise": None,
    }
    if lesson["type"] == "coding":
        exercise = EXERCISE_DIR / lesson["exercise"]
        payload["exercise"] = {
            "id": lesson["exercise"],
            "filename": "solution.py",
            "starter": (exercise / "starter.py").read_text(encoding="utf-8"),
        }
    return payload


def _solution_payload(lesson_id: str) -> dict | None:
    _, lesson = _find_lesson(lesson_id)
    if lesson is None or lesson.get("type") != "coding":
        return None
    path = EXERCISE_DIR / lesson["exercise"] / "solution.py"
    if not path.exists():
        return None
    return {"exercise": lesson["exercise"], "code": path.read_text(encoding="utf-8")}


# ---------------------------------------------------------------------------
# 代码执行
# ---------------------------------------------------------------------------
def _clip(text: str, limit: int = MAX_OUTPUT) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n…（输出超过 {limit} 字符，已截断）"


def _drain(stream, sink: list[str], limit: int) -> None:
    """持续读空管道，但只保留前 limit 个字符。

    死循环打印的代码会在 5 秒内产出几百 MB 输出，如果先 capture 再截断，
    内存会先爆掉。这里边读边丢，内存占用恒定。
    """
    kept = 0
    try:
        while True:
            chunk = stream.read(4096)
            if not chunk:
                break
            if kept < limit:
                piece = chunk[: limit - kept]
                sink.append(piece)
                kept += len(piece)
    except (OSError, ValueError):
        pass
    finally:
        try:
            stream.close()
        except OSError:
            pass


def _kill_tree(process: subprocess.Popen) -> None:
    """杀掉整个进程组，避免学员代码 fork 出的子进程残留。"""
    if os.name == "nt":
        process.kill()
        return
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            process.kill()
        except OSError:
            pass


def _execute(files: dict[str, str], entry: str, timeout: float) -> dict:
    """把文件写进临时目录并执行 entry，超时终止整个进程组。"""
    with tempfile.TemporaryDirectory(prefix="pylab-") as tmp_dir:
        tmp = Path(tmp_dir)
        for name, content in files.items():
            (tmp / name).write_text(content, encoding="utf-8")

        started = time.perf_counter()
        process = subprocess.Popen(
            [sys.executable, "-X", "utf8", entry],
            cwd=tmp,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            start_new_session=(os.name != "nt"),
        )
        stdout_parts: list[str] = []
        stderr_parts: list[str] = []
        readers = [
            # 多留 1 个字符，让 _clip 能识别出发生过截断并给出提示
            threading.Thread(target=_drain, args=(process.stdout, stdout_parts, MAX_OUTPUT + 1), daemon=True),
            threading.Thread(target=_drain, args=(process.stderr, stderr_parts, MAX_OUTPUT + 1), daemon=True),
        ]
        for reader in readers:
            reader.start()

        timed_out = False
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            _kill_tree(process)
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass

        for reader in readers:
            reader.join(timeout=2)

        elapsed = int((time.perf_counter() - started) * 1000)
        stdout = "".join(stdout_parts)
        stderr = "".join(stderr_parts)
        if timed_out:
            stderr = (stderr + f"\n运行超过 {timeout:.0f} 秒，已终止。").strip()
        return {
            "stdout": _clip(stdout),
            "stderr": _clip(stderr),
            "exit_code": None if timed_out else process.returncode,
            "duration_ms": elapsed,
            "timed_out": timed_out,
        }


def _parse_results(stdout: str):
    for line in reversed(stdout.splitlines()):
        if line.startswith(SENTINEL):
            try:
                payload = json.loads(line[len(SENTINEL):])
            except json.JSONDecodeError:
                return None
            return payload if isinstance(payload, list) else None
    return None


def _check_exercise(exercise_id: str, code: str) -> dict:
    exercise = EXERCISE_DIR / exercise_id
    files = {
        "solution.py": code,
        "tests.py": (exercise / "tests.py").read_text(encoding="utf-8"),
        "_harness.py": (EXERCISE_DIR / "_harness.py").read_text(encoding="utf-8"),
    }
    mock_service = EXERCISE_DIR / "_mock_service.py"
    if mock_service.exists():
        files["_mock_service.py"] = mock_service.read_text(encoding="utf-8")
    run = _execute(files, "tests.py", CHECK_TIMEOUT)
    results = _parse_results(run["stdout"])
    if results is None:
        return {
            "ok": False,
            "results": [],
            "error": "测试脚本没有正常结束。常见原因：语法错误、导入失败、或在模块顶层就抛了异常。",
            "stdout": run["stdout"],
            "stderr": run["stderr"],
        }
    ok = bool(results) and all(item.get("ok") for item in results)
    return {
        "ok": ok,
        "results": results,
        "error": "",
        "stdout": run["stdout"],
        "stderr": run["stderr"],
    }


def _set_progress(lesson_id: str, status: str) -> dict:
    with PROGRESS_LOCK:
        progress = _load_progress()
        if status == "done":
            progress[lesson_id] = {
                "status": "done",
                "updated": datetime.now().isoformat(timespec="seconds"),
            }
        else:
            progress.pop(lesson_id, None)
        _save_progress(progress)
        return progress


# ---------------------------------------------------------------------------
# HTTP 处理
# ---------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "PyLab/1.0"
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"{self.address_string()} - {fmt % args}\n")

    # -- 基础响应 ----------------------------------------------------------
    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: dict, status: int = 200) -> None:
        self._send(status, json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8")

    def _read_json(self) -> dict | None:
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            self._json({"error": "Content-Length 非法"}, 400)
            return None
        if length > 1_000_000:
            self._json({"error": "请求体过大"}, 413)
            return None
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json({"error": "请求体不是合法 JSON"}, 400)
            return None
        if not isinstance(payload, dict):
            self._json({"error": "请求体必须是 JSON 对象"}, 400)
            return None
        return payload

    # -- 路由 --------------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802
        try:
            self._handle_get()
        except Exception:
            traceback.print_exc()
            self._json({"error": "服务器内部错误，请查看终端日志"}, 500)

    def do_POST(self) -> None:  # noqa: N802
        try:
            self._handle_post()
        except Exception:
            traceback.print_exc()
            self._json({"error": "服务器内部错误，请查看终端日志"}, 500)

    def _handle_get(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            self._serve_static("index.html")
            return
        if path.startswith("/static/"):
            self._serve_static(path[len("/static/"):])
            return
        if path == "/api/curriculum":
            self._json(_curriculum_payload())
            return
        if path == "/api/lesson":
            lesson_id = (parse_qs(parsed.query).get("id") or [""])[0]
            payload = _lesson_payload(lesson_id)
            if payload is None:
                self._json({"error": "课程不存在"}, 404)
            else:
                self._json(payload)
            return
        if path == "/api/solution":
            lesson_id = (parse_qs(parsed.query).get("id") or [""])[0]
            payload = _solution_payload(lesson_id)
            if payload is None:
                self._json({"error": "这道练习暂无参考答案"}, 404)
            else:
                self._json(payload)
            return
        self._json({"error": "接口不存在"}, 404)

    def _handle_post(self) -> None:
        path = urlparse(self.path).path
        payload = self._read_json()
        if payload is None:
            return

        if path in {"/api/run", "/api/check"}:
            lesson_id = payload.get("lesson_id", "")
            code = payload.get("code", "")
            if not isinstance(code, str):
                self._json({"error": "code 必须是字符串"}, 400)
                return
            _, lesson = _find_lesson(lesson_id)
            if lesson is None or lesson.get("type") != "coding":
                self._json({"error": "课程不存在或不是编程题"}, 404)
                return
            if path == "/api/run":
                result = _execute({"solution.py": code}, "solution.py", RUN_TIMEOUT)
                self._json(result)
            else:
                result = _check_exercise(lesson["exercise"], code)
                if result["ok"]:
                    _set_progress(lesson_id, "done")
                self._json(result)
            return

        if path == "/api/progress":
            lesson_id = payload.get("lesson_id", "")
            status = payload.get("status", "")
            _, lesson = _find_lesson(lesson_id)
            if lesson is None:
                self._json({"error": "课程不存在"}, 404)
                return
            if status not in {"done", "todo"}:
                self._json({"error": "status 只能是 done 或 todo"}, 400)
                return
            _set_progress(lesson_id, status)
            self._json({"ok": True})
            return

        self._json({"error": "接口不存在"}, 404)

    def do_HEAD(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _serve_static(self, relative: str) -> None:
        target = (STATIC_DIR / relative).resolve()
        static_root = STATIC_DIR.resolve()
        if not target.is_relative_to(static_root) or not target.is_file():
            self._json({"error": "文件不存在"}, 404)
            return
        if target.name == "index.html":
            self._send(200, self._render_index(), "text/html; charset=utf-8")
            return
        mime = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if mime.startswith("text/") or mime in {"application/javascript", "application/json"}:
            mime += "; charset=utf-8"
        self._send(200, target.read_bytes(), mime)

    @staticmethod
    def _render_index() -> bytes:
        """给静态资源加 mtime 版本号，避免浏览器拿旧 CSS/JS。"""
        document = (STATIC_DIR / "index.html").read_text(encoding="utf-8")

        def version(name: str) -> str:
            path = STATIC_DIR / name
            return str(int(path.stat().st_mtime)) if path.exists() else "0"

        document = document.replace("{{CSS_VERSION}}", version("style.css"))
        document = document.replace("{{JS_VERSION}}", version("app.js"))
        return document.encode("utf-8")


def _make_server(preferred_port: int) -> tuple[ThreadingHTTPServer, int]:
    for port in range(preferred_port, preferred_port + 10):
        try:
            return ThreadingHTTPServer(("127.0.0.1", port), Handler), port
        except OSError:
            continue
    raise SystemExit(f"端口 {preferred_port}–{preferred_port + 9} 均被占用，请用 --port 指定其他端口")


def main() -> int:
    parser = argparse.ArgumentParser(description="PyLab 本地学习平台")
    parser.add_argument("--port", type=int, default=8000, help="监听端口，默认 8000")
    parser.add_argument("--no-open", action="store_true", help="不自动打开浏览器")
    args = parser.parse_args()

    server, port = _make_server(args.port)
    PORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    PORT_FILE.write_text(str(port), encoding="utf-8")
    url = f"http://127.0.0.1:{port}/"
    print(f"PyLab 已启动: {url}")
    print("按 Ctrl+C 停止\n")
    if not args.no_open:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")
    finally:
        server.server_close()
        for path, value in ((PID_FILE, str(os.getpid())), (PORT_FILE, str(port))):
            try:
                if path.exists() and path.read_text(encoding="utf-8").strip() == value:
                    path.unlink()
            except OSError:
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
