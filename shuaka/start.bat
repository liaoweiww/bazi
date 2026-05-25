@echo off
REM ============================================================
REM 签到系统启动脚本 (Windows)
REM 用法：双击 start.bat
REM 注意：读卡器监听需要管理员权限，右键 → 以管理员身份运行
REM ============================================================
cd /d "%~dp0"

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

python main.py %*
pause
