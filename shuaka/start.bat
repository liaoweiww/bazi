@echo off
REM ============================================================
REM 签到系统启动脚本 (Windows)
REM 用法：双击 start.bat
REM ============================================================
cd /d "%~dp0"

REM 检查依赖，缺失则自动安装
python -c "import pynput" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [安装] 正在安装依赖包...
    pip install -r requirements.txt -q
)

echo [启动] 签到叫号系统...
python main.py %*
pause
