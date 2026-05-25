#!/usr/bin/env python3
"""
身份证签到叫号系统 — 一键安装程序
自动检测环境 → 安装依赖 → 交互式配置 → 创建快捷方式
"""

import os
import sys
import json
import shutil
import subprocess
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IS_WIN = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"

# ── 工具函数 ──

def print_step(n, text):
    print(f"\n  [{n}] {text}")

def print_ok(text):
    print(f"  ✓ {text}")

def print_err(text):
    print(f"  ✗ {text}")

def print_info(text):
    print(f"  ℹ {text}")

def ask(text, default=""):
    if default:
        val = input(f"  ▸ {text} [{default}]: ").strip()
        return val if val else default
    return input(f"  ▸ {text}: ").strip()

def ask_yn(text, default_yes=True):
    hint = "Y/n" if default_yes else "y/N"
    val = input(f"  ▸ {text} [{hint}]: ").strip().lower()
    if not val:
        return default_yes
    return val in ("y", "yes")

def run(cmd, show_output=False):
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=not show_output,
            text=True, cwd=BASE_DIR
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)


# ── 各安装步骤 ──

def check_python():
    print_step(1, "检测 Python 环境")
    ver = sys.version_info
    print_ok(f"Python {ver.major}.{ver.minor}.{ver.micro}")
    if ver < (3, 7):
        print_err("需要 Python 3.7 或更高版本！")
        print_info("请从 https://python.org 下载安装")
        if IS_WIN:
            print_info("安装时请勾选 'Add Python to PATH'")
        sys.exit(1)

    # 检查 pip
    ok, _ = run(f'"{sys.executable}" -m pip --version')
    if ok:
        print_ok("pip 可用")
    else:
        print_err("pip 不可用，正在修复...")
        run(f'"{sys.executable}" -m ensurepip')


def install_deps():
    print_step(2, "安装 Python 依赖包")
    print_info("正在安装，可能需要 1-2 分钟...")

    ok, out = run(f'"{sys.executable}" -m pip install -r requirements.txt -q')
    if ok:
        print_ok("依赖安装完成")
    else:
        print_err("安装失败，尝试使用国内镜像...")
        ok, _ = run(
            f'"{sys.executable}" -m pip install -r requirements.txt -q '
            f'-i https://pypi.tuna.tsinghua.edu.cn/simple'
        )
        if ok:
            print_ok("依赖安装完成（清华镜像）")
        else:
            print_err("安装失败，请手动执行: pip install -r requirements.txt")


def configure():
    print_step(3, "系统配置")

    # 读取模板
    template_path = os.path.join(BASE_DIR, "config.yaml")
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 地点名
    print()
    location = ask("签到地点名称（如：北京办公室）", "总服务台")

    # 2. Excel 保存目录
    default_dir = os.path.join(BASE_DIR, "签到记录")
    if IS_WIN:
        # 尝试猜测百度网盘目录
        guess = os.path.expanduser(r"~\BaiduSyncDisk\签到记录")
        if os.path.exists(os.path.dirname(guess)):
            default_dir = guess
    elif IS_MAC:
        guess = os.path.expanduser("~/BaiduSyncDisk/签到记录")
        if os.path.exists(os.path.dirname(guess)):
            default_dir = guess

    excel_dir = ask("签到记录保存目录", default_dir)

    # 3. 端口
    port = ask("Web 服务端口号", "5002")

    # 4. 语音
    voice_enabled = ask_yn("启用语音播报？", True)

    # 5. 外网访问
    print()
    print_info("如需平板上外网也能访问，可配置 ngrok 内网穿透（免费）")
    print_info("  1) 注册 https://ngrok.com")
    print_info("  2) 获取 Authtoken")
    ngrok_enabled = ask_yn("现在配置 ngrok？", False)
    ngrok_token = ""
    if ngrok_enabled:
        ngrok_token = ask("ngrok Authtoken", "")

    # 写入配置
    content = content.replace('location: "A地点"', f'location: "{location}"')
    content = content.replace('excel_dir: "./签到记录"', f'excel_dir: "{excel_dir}"')
    content = content.replace("port: 5002", f"port: {port}")
    content = content.replace("enabled: true", f"enabled: {str(voice_enabled).lower()}" if "voice:" in content.split("ngrok:")[0] else "enabled: true")
    content = re.sub(r'(ngrok:\n  enabled: )\w+', f'\\g<1>{str(ngrok_enabled).lower()}', content)
    if ngrok_token:
        content = re.sub(r'(ngrok:\n  enabled: \w+\n  auth_token: )""', f'\\g<1>"{ngrok_token}"', content)

    config_path = os.path.join(BASE_DIR, "config.yaml")
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)
    print_ok(f"配置已保存: {config_path}")

    # 确保 Excel 目录存在
    os.makedirs(excel_dir, exist_ok=True)
    print_ok(f"数据目录已创建: {excel_dir}")

    return location, excel_dir


def create_shortcuts():
    print_step(4, "创建快捷方式")

    if IS_MAC:
        # 创建桌面启动脚本
        desktop = os.path.expanduser("~/Desktop")
        launcher = os.path.join(desktop, "签到系统.command")
        with open(launcher, "w") as f:
            f.write(f'#!/bin/bash\ncd "{BASE_DIR}"\n"{sys.executable}" main.py\n')
        os.chmod(launcher, 0o755)
        print_ok(f"桌面快捷方式已创建: {launcher}")

    elif IS_WIN:
        # 创建桌面快捷方式
        try:
            import pythoncom
            from win32com.client import Dispatch
            pythoncom.CoInitialize()
            shell = Dispatch("WScript.Shell")
            desktop = shell.SpecialFolders("Desktop")
            shortcut_path = os.path.join(desktop, "签到系统.lnk")
            shortcut = shell.CreateShortcut(shortcut_path)
            shortcut.TargetPath = os.path.join(BASE_DIR, "start.bat")
            shortcut.WorkingDirectory = BASE_DIR
            shortcut.IconLocation = sys.executable
            shortcut.Save()
            pythoncom.CoUninitialize()
            print_ok(f"桌面快捷方式已创建: {shortcut_path}")
        except ImportError:
            # win32com 不可用，复制 bat 到桌面
            desktop = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
            bat_dest = os.path.join(desktop, "签到系统.bat")
            shutil.copy(os.path.join(BASE_DIR, "start.bat"), bat_dest)
            print_ok(f"已将启动脚本复制到桌面: {bat_dest}")

    # 创建快捷启动方式（当前目录）
    if IS_MAC:
        quick = os.path.join(BASE_DIR, "启动签到系统.command")
        with open(quick, "w") as f:
            f.write(f'#!/bin/bash\ncd "{BASE_DIR}"\n"{sys.executable}" main.py\n')
        os.chmod(quick, 0o755)


def verify():
    print_step(5, "验证安装")

    # 检查关键依赖
    deps_ok = True
    required = ["openpyxl", "flask", "yaml"]
    if IS_WIN:
        required.append("pyttsx3")
    else:
        required.append("pynput")
    for mod in required:
        try:
            __import__(mod)
        except ImportError:
            print_err(f"模块 {mod} 导入失败")
            deps_ok = False

    if deps_ok:
        print_ok("所有依赖模块正常")
    else:
        print_err("部分依赖异常，请手动执行: pip install -r requirements.txt")
        return False

    # 测试无错误导入自己的模块
    for mod_name in ["excel_manager", "voice_broadcast", "timer_manager", "card_listener", "web_server"]:
        try:
            spec = __import__("importlib.util").util.spec_from_file_location(
                mod_name, os.path.join(BASE_DIR, f"{mod_name}.py")
            )
            if spec is None:
                print_err(f"找不到模块文件: {mod_name}.py")
                deps_ok = False
        except Exception:
            pass

    if deps_ok:
        print_ok("所有模块文件完整")
    return deps_ok


def show_completion(location, excel_dir):
    print()
    print("=" * 55)
    print("  ✅ 安装完成！")
    print("=" * 55)
    print()
    print("  启动方式：")
    if IS_WIN:
        print(f"    双击桌面的「签到系统」快捷方式")
        print(f"    或双击 shuaka/ 目录下的 start.bat")
    else:
        print(f"    双击桌面的「签到系统.command」")
        print(f"    或终端执行: cd shuaka && python3 main.py")
    print()
    print("  启动后：")
    print(f"    叫号大屏:  http://你的IP:5002")
    print(f"    后台管理:  http://你的IP:5002/admin")
    print(f"    数据目录:  {excel_dir}")
    print()
    print("  详细使用说明请阅读：部署说明.md")
    print()


# ── 主流程 ──

def main():
    print()
    print("=" * 55)
    print("   身份证签到叫号系统 — 安装程序")
    print("=" * 55)

    if not (IS_WIN or IS_MAC):
        print()
        print_err("暂不支持当前操作系统")
        print_info("请手动执行: pip install -r requirements.txt")
        print_info("然后编辑 config.yaml 配置文件")
        sys.exit(1)

    steps = [
        ("检测 Python 环境", check_python),
        ("安装依赖包", install_deps),
        ("系统配置", configure),
        ("创建快捷方式", create_shortcuts),
        ("验证安装", verify),
    ]

    location = ""
    excel_dir = ""

    for name, func in steps:
        try:
            result = func()
            if name == "系统配置":
                location, excel_dir = result
        except KeyboardInterrupt:
            print("\n\n安装已取消。")
            sys.exit(0)
        except Exception as e:
            print_err(f"{name} 失败: {e}")
            if name != "创建快捷方式":
                print_info("请解决上述问题后重新运行安装程序")
                sys.exit(1)

    show_completion(location, excel_dir)

    # 询问是否立即启动
    if ask_yn("是否现在启动签到系统？", True):
        print()
        print_info("正在启动...")
        if IS_WIN:
            subprocess.Popen(
                [sys.executable, "main.py", "--no-ngrok"],
                cwd=BASE_DIR
            )
        else:
            subprocess.Popen(
                [sys.executable, "main.py", "--no-ngrok"],
                cwd=BASE_DIR
            )
        print_info("系统已在后台启动！请打开浏览器访问管理后台。")


if __name__ == "__main__":
    main()
