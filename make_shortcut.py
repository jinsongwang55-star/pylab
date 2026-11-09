#!/usr/bin/env python3
"""在当前用户桌面创建 PyLab 启动快捷方式。

用法:
    python3 make_shortcut.py

Linux   -> ~/Desktop/PyLab.desktop（无终端窗口）
macOS   -> ~/Desktop/PyLab.app（无终端窗口）
Windows -> ~/Desktop/PyLab.vbs（无 cmd 窗口）
"""

from __future__ import annotations

import platform
import shutil
import stat
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAUNCH_SH = ROOT / "launch.sh"

MACOS_INFO_PLIST = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>PyLab</string>
    <key>CFBundleIdentifier</key>
    <string>local.pylab.launcher</string>
    <key>CFBundleName</key>
    <string>PyLab</string>
    <key>CFBundleDisplayName</key>
    <string>PyLab</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSUIElement</key>
    <true/>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
"""


def desktop_dir() -> Path:
    if platform.system() == "Windows":
        try:
            import ctypes

            buffer = ctypes.create_unicode_buffer(260)
            # CSIDL_DESKTOPDIRECTORY = 0x0010，能正确解析 OneDrive 重定向的桌面
            if ctypes.windll.shell32.SHGetFolderPathW(None, 0x0010, None, 0, buffer) == 0:
                return Path(buffer.value)
        except Exception:  # noqa: BLE001
            pass
    home = Path.home()
    for name in ("Desktop", "桌面"):
        candidate = home / name
        if candidate.is_dir():
            return candidate
    return home / "Desktop"


def make_linux(target: Path) -> Path:
    shortcut = target / "PyLab.desktop"
    shortcut.write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Version=1.0\n"
        "Name=PyLab\n"
        "Comment=Python 学习与验证平台\n"
        f'Exec="{LAUNCH_SH}"\n'
        "Icon=utilities-terminal\n"
        "Terminal=false\n"
        "Categories=Education;Development;\n",
        encoding="utf-8",
    )
    shortcut.chmod(shortcut.stat().st_mode | stat.S_IXUSR)
    # GNOME 需要 trusted 标记；没有 gio 或失败都不影响文件生成
    subprocess.run(
        ["gio", "set", str(shortcut), "metadata::trusted", "true"],
        capture_output=True,
        check=False,
    )
    return shortcut


def make_macos(target: Path) -> Path:
    """生成最小 .app 包：双击不打开终端，LSUIElement 隐藏 Dock 图标。"""
    app = target / "PyLab.app"
    if app.is_symlink() or app.is_file():
        app.unlink()
    elif app.exists():
        shutil.rmtree(app)

    contents = app / "Contents"
    macos_dir = contents / "MacOS"
    macos_dir.mkdir(parents=True)
    (contents / "Info.plist").write_text(MACOS_INFO_PLIST, encoding="utf-8")

    launcher = macos_dir / "PyLab"
    launcher.write_text(
        "#!/bin/bash\n"
        f'cd "{ROOT}" || exit 1\n'
        "exec /bin/bash ./launch.sh\n",
        encoding="utf-8",
    )
    launcher.chmod(0o755)
    return app


def make_windows(target: Path) -> Path:
    # VBS 用 UTF-16 保存，WSH 才能正确读取中文路径
    shortcut = target / "PyLab.vbs"
    shortcut.write_text(
        "' PyLab silent launcher\r\n"
        'Set shell = CreateObject("WScript.Shell")\r\n'
        f'projectDir = "{ROOT}"\r\n'
        'shell.CurrentDirectory = projectDir\r\n'
        'cmd = """" & projectDir & "\\launch.bat"" --silent"\r\n'
        'rc = shell.Run(cmd, 0, True)\r\n'
        'If rc <> 0 Then\r\n'
        '    MsgBox "PyLab 启动失败，请查看 data\\server.log", 16, "PyLab"\r\n'
        'End If\r\n',
        encoding="utf-16",
    )
    return shortcut


def main() -> int:
    system = platform.system()
    target = desktop_dir()
    target.mkdir(parents=True, exist_ok=True)

    if system == "Linux":
        path = make_linux(target)
    elif system == "Darwin":
        path = make_macos(target)
    elif system == "Windows":
        path = make_windows(target)
    else:
        print(f"暂不支持该系统: {system}")
        return 1

    print(f"已创建快捷方式: {path}")
    print("双击即可静默启动 PyLab，浏览器会自动打开。")
    print("启动日志: data/server.log")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
