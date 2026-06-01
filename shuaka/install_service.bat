@echo off
chcp 65001 >nul
echo ============================================
echo   身份证签到系统 - 开机自启安装
echo ============================================
echo.
echo 正在创建计划任务（开机自启 + 管理员权限）...

set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

schtasks /create /tn "签到系统" /tr "python -u \"%SCRIPT_DIR%\main.py\"" /sc onstart /rl highest /f

if %errorlevel%==0 (
    echo.
    echo ✅ 安装成功！下次开机自动以管理员身份启动。
    echo.
    echo 现在启动服务...
    schtasks /run /tn "签到系统"
    echo.
    echo 服务已启动，浏览器打开 http://127.0.0.1:5002
) else (
    echo.
    echo ❌ 安装失败，请以管理员身份运行此脚本
)
pause
