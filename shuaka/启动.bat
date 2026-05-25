@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo [检查] 依赖环境...

python -c "import openpyxl,flask,yaml,pyttsx3" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [安装] 缺少依赖，正在安装...
    pip install openpyxl flask pyyaml pyttsx3 -q
    if %ERRORLEVEL% neq 0 (
        echo [错误] 安装失败，请检查网络
        pause
        exit /b 1
    )
    echo [完成] 依赖安装完毕
)

echo.
echo ============================================
echo   签到叫号系统 v1.0
echo ============================================
echo.

python main.py %*
pause
