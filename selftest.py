#!/usr/bin/env python3
"""开发者自检：用 exercises/<id>/solution.py 跑通全部练习，并检查课程完整性。

用法:
    python selftest.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown_render

ROOT = Path(__file__).resolve().parent
EXERCISES = ROOT / "exercises"
CONTENT = ROOT / "content"
SENTINEL = "__PYLAB_RESULTS__"


def load_curriculum() -> dict:
    return json.loads((ROOT / "curriculum.json").read_text(encoding="utf-8"))


def run_exercise(exercise_id: str, code: str) -> tuple[bool, list[dict], str]:
    directory = EXERCISES / exercise_id
    with tempfile.TemporaryDirectory(prefix="pylab-self-") as tmp_dir:
        tmp = Path(tmp_dir)
        (tmp / "solution.py").write_text(code, encoding="utf-8")
        (tmp / "tests.py").write_text((directory / "tests.py").read_text(encoding="utf-8"), encoding="utf-8")
        (tmp / "_harness.py").write_text(
            (EXERCISES / "_harness.py").read_text(encoding="utf-8"), encoding="utf-8"
        )
        mock_service = EXERCISES / "_mock_service.py"
        if mock_service.exists():
            (tmp / "_mock_service.py").write_text(
                mock_service.read_text(encoding="utf-8"), encoding="utf-8"
            )
        proc = subprocess.run(
            [sys.executable, "tests.py"],
            cwd=tmp,
            capture_output=True,
            text=True,
            timeout=30,
        )
    results = []
    for line in reversed(proc.stdout.splitlines()):
        if line.startswith(SENTINEL):
            results = json.loads(line[len(SENTINEL):])
            break
    return bool(results) and all(item["ok"] for item in results), results, proc.stderr


def check_content(curriculum: dict) -> tuple[list[str], list[dict]]:
    problems: list[str] = []
    coding_lessons: list[dict] = []
    for stage in curriculum["stages"]:
        for lesson in stage.get("lessons", []):
            content = CONTENT / lesson["file"]
            if not content.exists():
                problems.append(f"缺少课程文件: {content}")
                continue
            html = markdown_render.render(content.read_text(encoding="utf-8"))
            if len(html) < 200:
                problems.append(f"渲染结果过短: {lesson['file']}")
            if "```" in html:
                problems.append(f"代码围栏未被解析: {lesson['file']}")
            if lesson["type"] != "coding":
                continue
            coding_lessons.append(lesson)
            exercise = EXERCISES / lesson["exercise"]
            for name in ("starter.py", "tests.py", "solution.py"):
                if not (exercise / name).exists():
                    problems.append(f"缺少练习文件: {exercise / name}")
    return problems, coding_lessons


def main() -> int:
    failures = 0
    curriculum = load_curriculum()

    print("课程文件检查")
    print("=" * 60)
    problems, coding_lessons = check_content(curriculum)
    if problems:
        failures += len(problems)
        for problem in problems:
            print(f"[FAIL] {problem}")
    else:
        print(f"[PASS] {len(coding_lessons)} 组练习文件齐全，Markdown 渲染正常")

    print("\n参考答案验证")
    print("=" * 60)
    for lesson in coding_lessons:
        exercise_id = lesson["exercise"]
        exercise_dir = EXERCISES / exercise_id
        solution_file = exercise_dir / "solution.py"
        starter_file = exercise_dir / "starter.py"
        if not solution_file.exists():
            failures += 1
            print(f"[FAIL] 练习 {exercise_id}: 没有 solution.py")
            continue
        ok, results, stderr = run_exercise(exercise_id, solution_file.read_text(encoding="utf-8"))
        passed = sum(1 for item in results if item["ok"])
        total = len(results)
        if ok:
            print(f"[PASS] 练习 {exercise_id}: {passed}/{total}")
        else:
            failures += 1
            print(f"[FAIL] 练习 {exercise_id}: {passed}/{total}")
            for item in results:
                if not item["ok"]:
                    print(f"       - {item['name']}: {item['msg']}")
            if not results:
                print(f"       stderr: {stderr.strip()[:400]}")

        # 起始代码必须无法通过，否则等于白送答案
        starter_ok, _, _ = run_exercise(exercise_id, starter_file.read_text(encoding="utf-8"))
        if starter_ok:
            failures += 1
            print(f"[FAIL] 练习 {exercise_id}: 起始代码不应通过测试")

    print("\n" + "=" * 60)
    if failures:
        print(f"自检失败，共 {failures} 个问题。")
        return 1
    print("自检全部通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
