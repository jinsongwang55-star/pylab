#!/usr/bin/env bash
# PyLab 启动入口：实际逻辑在 launcher.py，Windows 走同一套。
set -u
cd "$(dirname "$0")" || exit 1

PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "未找到 python3。请先安装 Python 3.10 或更高版本。"
    if [ -t 0 ]; then
        read -r -p "按回车键关闭..." _
    fi
    exit 1
fi

exec "$PYTHON" launcher.py
