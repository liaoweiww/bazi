@echo off
chcp 65001 >nul
REM ============================================================
REM 签到系统启动脚本 (Windows)
REM 用法：右键 → 以管理员身份运行
REM 读卡器监听需管理员 + 网络盘需先设 EnableLinkedConnections
REM ============================================================
cd /d "%~dp0"

if not exist "main.py" (
    echo [错误] 找不到 main.py，请确保在 shuaka 目录下运行
    pause
    exit /b 1
)

REM 检查依赖，缺失则自动安装
python -c "import openpyxl,flask,yaml" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [安装] 正在安装依赖包...
    pip install -r requirements.txt -q
)

REM 检查 Windows TTS 依赖
python -c "import pyttsx3" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [安装] 正在安装语音引擎...
    pip install pyttsx3 -q
)

echo.
echo ============================================
echo   签到叫号系统 v1.0 - Windows
echo   读卡器: Win USB 底层钩子模式
echo   语音: SAPI5 TTS 引擎
echo ============================================
echo.

REM 将 Python 字节码缓存重定向到本机目录，避免百度云跨平台同步冲突
set PYTHONPYCACHEPREFIX=%LOCALAPPDATA%\shuaka\pycache

python main.py %*
pause
