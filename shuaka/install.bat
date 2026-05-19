@echo off
chcp 65001 >nul
REM ============================================================
REM 签到系统一键安装脚本 (Windows)
REM 用法：双击 install.bat
REM ============================================================

cd /d "%~dp0"

echo.
echo ===========================================
echo   签到叫号系统 - Windows 安装
echo ===========================================

REM 检查 Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo.
    echo   ✗ 未检测到 Python
    echo   请先安装 Python 3.7+：
    echo   https://python.org
    echo   ⚠ 安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYVER=%%i
echo   ✓ 检测到 %PYVER%

REM 运行安装程序
python install.py

echo.
echo 安装脚本执行完毕。
pause
