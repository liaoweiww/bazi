"""
跨平台工具模块
自动识别 macOS / Windows / Linux，提供统一接口
"""

import os
import sys
import platform
import subprocess

# ========== 系统识别 ==========
IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"
IS_LINUX = sys.platform.startswith("linux")
SYSTEM = platform.system()  # "Darwin" / "Windows" / "Linux"
MACHINE = platform.machine()  # "arm64" / "x86_64" / "AMD64"


# ========== 路径工具 ==========

def _get_machine_config():
    """读取本机专属配置 machine.json"""
    try:
        import json
        if IS_WIN:
            local_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'shuaka')
        else:
            local_dir = os.path.join(os.path.expanduser('~'), '.shuaka')
        path = os.path.join(local_dir, 'machine.json')
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def get_baidu_sync_dir():
    """获取百度网盘同步目录（优先使用本机配置）"""
    # 1. 优先检查本机配置中手动设置的路径
    machine = _get_machine_config()
    custom = machine.get("baidu_sync_dir", "")
    if custom and os.path.isdir(custom):
        return custom

    # 2. 自动检测常见路径
    if IS_WIN:
        candidates = [
            os.path.expanduser(r"~\BaiduSyncDisk"),
            os.path.expanduser(r"~\BaiduNetdisk"),
            r"D:\BaiduSyncDisk",
            r"E:\BaiduSyncDisk",
        ]
    elif IS_MAC:
        candidates = [
            os.path.expanduser("~/BaiduSyncDisk"),
            os.path.expanduser("~/BaiduNetdisk"),
        ]
    else:
        candidates = [os.path.expanduser("~/BaiduSyncDisk")]

    for path in candidates:
        if os.path.isdir(path):
            return path
    return candidates[0]  # 返回第一个作为默认


def get_sync_data_dir(base_dir=None):
    """
    获取多机同步数据根目录
    固定使用项目下的 BaiduSyncdisk/ 目录，用户将百度云同步文件夹指向此目录即可
    """
    if base_dir is None:
        import __main__
        base_dir = os.path.dirname(os.path.abspath(__main__.__file__)) if hasattr(__main__, '__file__') else os.getcwd()
    sync_root = os.path.join(base_dir, "BaiduSyncdisk")
    os.makedirs(sync_root, exist_ok=True)
    placeholder = os.path.join(sync_root, ".syncing")
    if not os.path.exists(placeholder):
        with open(placeholder, "w", encoding="utf-8") as f:
            f.write("签到系统数据同步目录\n")
    return sync_root


def get_desktop_dir():
    """获取桌面目录"""
    if IS_WIN:
        return os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Desktop")
    return os.path.expanduser("~/Desktop")


def get_data_dir(default="./签到记录"):
    """获取签到数据存储目录（优先百度网盘同步目录）"""
    sync = get_sync_data_dir()
    if sync:
        data_dir = os.path.join(sync, "签到记录")
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    return default


def get_ngrok_path():
    """获取 ngrok 可执行文件路径"""
    if IS_WIN:
        candidates = [
            "ngrok.exe",
            os.path.expanduser(r"~\ngrok\ngrok.exe"),
            r"C:\ngrok\ngrok.exe",
        ]
    elif IS_MAC:
        candidates = [
            "ngrok",
            "/usr/local/bin/ngrok",
            "/opt/homebrew/bin/ngrok",
            os.path.expanduser("~/ngrok"),
        ]
    else:
        candidates = ["ngrok"]

    for c in candidates:
        try:
            result = subprocess.run([c, "version"], capture_output=True, timeout=5)
            if result.returncode == 0:
                return c
        except Exception:
            continue
    return None


def get_python_cmd():
    """获取 Python 解释器命令"""
    return "python" if IS_WIN else "python3"


def get_start_script():
    """获取系统对应的启动脚本名"""
    return "start.bat" if IS_WIN else "start.sh"


# ========== 硬件信息 ==========

def get_mac_address():
    """获取本机 MAC 地址（用于设备识别）"""
    import uuid
    return ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff)
                     for i in range(0, 48, 8)][::-1])


# ========== 调试信息 ==========

def print_env():
    """打印当前运行环境"""
    print(f"  操作系统: {SYSTEM} ({MACHINE})")
    print(f"  Python:   {sys.version.split()[0]}")
    print(f"  工作目录: {os.getcwd()}")
    baidu = get_baidu_sync_dir()
    print(f"  百度网盘: {'已检测到 ' + baidu if os.path.isdir(baidu) else '未检测到'}")
    ngrok = get_ngrok_path()
    print(f"  ngrok:    {ngrok or '未找到'}")

