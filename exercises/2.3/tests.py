import io
from contextlib import redirect_stderr
from pathlib import Path

import solution
from _harness import run


def _parser():
    return solution.build_parser()


def test_organize_basic():
    args = _parser().parse_args(["organize", "--path", "downloads"])
    assert args.command == "organize", f"command 应为 organize，实际 {args.command!r}"
    assert args.path == Path("downloads"), f"path 应为 Path 对象，实际 {type(args.path).__name__}"
    assert args.dry_run is False, "dry_run 默认应为 False"


def test_dry_run_flag():
    args = _parser().parse_args(["organize", "--path", "x", "--dry-run"])
    assert args.dry_run is True, "--dry-run 应把 dry_run 设为 True"


def test_undo():
    args = _parser().parse_args(["undo", "--path", "x"])
    assert args.command == "undo"
    assert args.path == Path("x")


def test_missing_path():
    with redirect_stderr(io.StringIO()):
        try:
            _parser().parse_args(["organize"])
        except SystemExit:
            return
    raise AssertionError("缺少 --path 时应报错退出")


def test_missing_subcommand():
    with redirect_stderr(io.StringIO()):
        try:
            _parser().parse_args([])
        except SystemExit:
            return
    raise AssertionError("未提供子命令时应报错退出")


run([
    ("organize 参数解析", test_organize_basic),
    ("--dry-run 开关", test_dry_run_flag),
    ("undo 参数解析", test_undo),
    ("缺少 --path 时报错", test_missing_path),
    ("缺少子命令时报错", test_missing_subcommand),
])
