@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "OUT=diagnose.txt"

echo PyLab Windows 环境诊断 > "%OUT%"
echo 时间: %date% %time% >> "%OUT%"
echo 目录: %CD% >> "%OUT%"
echo. >> "%OUT%"

echo [Python Launcher] >> "%OUT%"
where py >> "%OUT%" 2>&1
py -3 -V >> "%OUT%" 2>&1
echo. >> "%OUT%"

echo [Python PATH] >> "%OUT%"
where python >> "%OUT%" 2>&1
echo. >> "%OUT%"

echo [关键文件] >> "%OUT%"
dir /b server.py launcher.py stop.py launch.bat launch.vbs check_windows.bat >> "%OUT%" 2>&1
echo. >> "%OUT%"

echo [8000 端口占用] >> "%OUT%"
netstat -ano | findstr ":8000" >> "%OUT%" 2>&1
echo. >> "%OUT%"

type "%OUT%"
echo.
echo 结果已写入 diagnose.txt，请把它发回。
pause
