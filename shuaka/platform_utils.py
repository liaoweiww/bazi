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

def get_baidu_sync_dir():
    """获取百度网盘同步目录"""
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


def get_desktop_dir():
    """获取桌面目录"""
    if IS_WIN:
        return os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Desktop")
    return os.path.expanduser("~/Desktop")


def get_data_dir(default="./签到记录"):
    """获取签到数据存储目录（优先百度网盘）"""
    baidu = get_baidu_sync_dir()
    if os.path.isdir(baidu):
        data_dir = os.path.join(baidu, "签到记录")
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

