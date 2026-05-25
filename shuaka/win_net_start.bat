@echo off
chcp 65001 >nul
REM ============================================================
REM 签到系统 - 网络共享启动脚本 (Windows)
REM 从 Mac 共享文件夹直接运行，无需拷贝代码
REM 用法：双击本文件即可
REM ============================================================

set MAC_IP=192.168.50.226
set SHARE_NAME=shuaka
set DRIVE_LETTER=Z:

echo.
echo ============================================
echo   签到叫号系统 - 网络共享模式
echo   代码源: Mac (%MAC_IP%)
echo   本地盘符: %DRIVE_LETTER%
echo ============================================
echo.

REM 先断开旧映射（如果存在）
net use %DRIVE_LETTER% /delete >nul 2>nul

REM 挂载 Mac 共享目录
echo [挂载] 正在连接 Mac 共享目录...
net use %DRIVE_LETTER% \\%MAC_IP%\%SHARE_NAME% /persistent:no

if %ERRORLEVEL% neq 0 (
    echo.
    echo   ✗ 连接失败！请检查：
    echo   1. Mac 端是否已开启文件共享
    echo   2. Mac IP 是否正确: %MAC_IP%
    echo   3. 两台电脑是否在同一网络
    echo.
    pause
    exit /b 1
)

echo   ✓ 已连接 \\%MAC_IP%\%SHARE_NAME% → %DRIVE_LETTER%

REM 切换到共享目录
%DRIVE_LETTER%
cd \

REM 检查依赖
echo.
echo [检查] Python 环境与依赖...
python -c "import openpyxl,flask,yaml" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [安装] 正在安装依赖...
    pip install -r requirements.txt -q
)

python -c "import pyttsx3" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    pip install pyttsx3 -q
)

echo.
echo ============================================
echo   启动签到系统...
echo   网络共享模式 - 代码实时同步 Mac
echo ============================================
echo.

python main.py %*

pause

REM 退出时断开映射
net use %DRIVE_LETTER% /delete >nul 2>nul
