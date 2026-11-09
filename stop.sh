#!/usr/bin/env bash
# PyLab 停止入口：实际逻辑在 stop.py。
set -u
cd "$(dirname "$0")" || exit 1

PYTHON="${PYTHON:-python3}"
exec "$PYTHON" stop.py
