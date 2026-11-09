"""2.3 参考答案：为 filesorter 构建命令行解析器。"""

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="filesorter", description="按扩展名整理文件")
    sub = parser.add_subparsers(dest="command", required=True)

    organize = sub.add_parser("organize", help="整理目录")
    organize.add_argument("--path", type=Path, required=True, help="要整理的目录")
    organize.add_argument("--dry-run", action="store_true", help="只预演，不改动文件")

    undo = sub.add_parser("undo", help="撤销整理")
    undo.add_argument("--path", type=Path, required=True, help="撤销范围目录")

    return parser
