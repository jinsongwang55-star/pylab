@echo off
chcp 65001 >nul
cd /d "%~dp0"

set "SILENT=0"
if /i "%~1"=="--silent" set "SILENT=1"
if not exist data mkdir data

set "PY="
where py >nul 2>nul && set "PY=py -3"
if defined PY goto have_python

where python >nul 2>nul
if errorlevel 1 goto no_python

set "PY_PATH="
for /f "delims=" %%P in ('where python') do set "PY_PATH=%%P"
echo %PY_PATH% | findstr /i "WindowsApps" >nul
if not errorlevel 1 goto store_python

set "PY=python"
goto have_python

:no_python
echo [%date% %time%] 未找到 Python。请安装 Python 3.10+ 并勾选 Add to PATH。>> data\server.log
echo 未找到 Python。请安装 Python 3.10+ 并勾选 Add to PATH。
if "%SILENT%"=="0" pause
exit /b 1

:store_python
echo [%date% %time%] 检测到 Microsoft Store 的 Python 占位程序，请安装 python.org 版本。>> data\server.log
echo 检测到 Microsoft Store 的 Python 占位程序。
echo 请从 python.org 安装 Python，并在安装时勾选 Add Python to PATH。
if "%SILENT%"=="0" pause
exit /b 1

:have_python
%PY% launcher.py
set "RC=%errorlevel%"
if "%RC%"=="0" exit /b 0
echo [%date% %time%] 启动器退出码 %RC%，详见 data\server.log。>> data\server.log
if "%SILENT%"=="0" pause
exit /b %RC%
