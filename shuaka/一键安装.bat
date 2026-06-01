@echo off
chcp 65001 >nul
title 签到叫号系统 - 一键安装
color 0A

REM ============================================================
REM  签到叫号系统 — Windows 一键安装程序
REM  功能：检测环境 → 安装依赖 → 配置路径 → 创建快捷方式 → 启动服务
REM  用法：右键 → 以管理员身份运行
REM ============================================================

cd /d "%~dp0"
set "INSTALL_DIR=%~dp0"

echo.
echo   ╔══════════════════════════════════════════╗
echo   ║    身份证签到叫号系统 — 一键安装         ║
echo   ║    Windows 版 v2.0                        ║
echo   ╚══════════════════════════════════════════╝
echo.

REM ====== 1. 检测 Python ======
echo [1/5] 检测 Python 环境...
set PYTHON=

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set "PYVER=%%i"
    echo   ✓ 已安装: %PYVER%
    goto :check_pip
)

echo   ! 未检测到 Python，尝试自动安装...
winget install Python.Python.3.12 --silent --accept-package-agreements >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo   ✓ Python 安装完成，请重启此脚本
    pause
    exit /b 0
)

echo.
echo   ✗ 自动安装失败
echo   ─────────────────────────────────────
echo   请手动安装 Python:
echo   1. 打开浏览器访问 https://python.org
echo   2. 下载 Python 3.9+ Windows installer
echo   3. 安装时务必勾选 "Add Python to PATH"
echo   4. 安装完成后重新运行本脚本
echo   ─────────────────────────────────────
start https://python.org
pause
exit /b 1

:check_pip
python -m pip --version >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo   ! 正在修复 pip...
    python -m ensurepip --upgrade
)

REM ====== 2. 安装依赖 ======
echo.
echo [2/5] 安装 Python 依赖包...

python -m pip install -r requirements.txt -q -i https://pypi.tuna.tsinghua.edu.cn/simple 2>nul
if %ERRORLEVEL% neq 0 (
    python -m pip install -r requirements.txt -q
)

if %ERRORLEVEL% neq 0 (
    echo   ✗ 依赖安装失败，请检查网络连接
    pause
    exit /b 1
)
echo   ✓ 依赖安装完成

REM ====== 3. 初始配置 ======
echo.
echo [3/5] 配置系统参数...

REM 检查 Python 模块是否正常
python -c "import openpyxl,flask,yaml; print('OK')" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo   ✗ 模块加载失败
    pause
    exit /b 1
)
echo   ✓ 配置就绪

REM ====== 4. 创建快捷方式 ======
echo.
echo [4/5] 创建桌面快捷方式...

set "DESKTOP=%USERPROFILE%\Desktop"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

set "VBS=%TEMP%\create_shortcut.vbs"
(
echo Set ws = CreateObject("WScript.Shell"^)
echo desktop = ws.SpecialFolders("Desktop"^)
echo Set shortcut = ws.CreateShortcut(desktop ^& "\签到叫号系统.lnk"^)
echo shortcut.TargetPath = "%INSTALL_DIR%start.bat"
echo shortcut.WorkingDirectory = "%INSTALL_DIR%"
echo shortcut.Description = "身份证签到叫号系统"
echo shortcut.IconLocation = "%INSTALL_DIR%tablet\icon.ico,0"
echo shortcut.Save
echo Set startupShortcut = ws.CreateShortcut("%STARTUP_DIR%\签到叫号系统.lnk"^)
echo startupShortcut.TargetPath = "%INSTALL_DIR%start.bat"
echo startupShortcut.WorkingDirectory = "%INSTALL_DIR%"
echo startupShortcut.Save
) > "%VBS%"

cscript //nologo "%VBS%" >nul 2>nul
del "%VBS%" >nul 2>nul

echo   ✓ 桌面快捷方式已创建
echo   ✓ 开机自启动已设置

REM ====== 5. 启动服务 ======
echo.
echo [5/5] 启动签到系统...
echo.
echo   ╔══════════════════════════════════════════╗
echo   ║  系统正在启动...                         ║
echo   ║  大屏页面: http://localhost:5002          ║
echo   ║  管理后台: http://localhost:5002/admin    ║
echo   ║  默认账号: admin / admin123               ║
echo   ║  关闭窗口或按 Ctrl+C 停止服务             ║
echo   ╚══════════════════════════════════════════╝
echo.

start http://localhost:5002
python desktop_app.py

echo.
echo 系统已停止。
pause
