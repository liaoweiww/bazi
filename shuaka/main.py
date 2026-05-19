#!/usr/bin/env python3
"""
身份证签到系统 — 主程序入口
- 后台监听 USB 身份证读卡器
- 自动生成 Excel 签到记录
- 离线语音播报 + 40分钟提醒
- 本地 Web 服务器 + 管理后台 (/admin)
- 支持 ngrok 内网穿透实现外网访问

启动方式：
    python main.py
    python main.py --config /path/to/config.yaml
"""

import os
import sys
import json
import time
import signal
import argparse
import logging
import subprocess
import threading

import yaml

from excel_manager import ExcelManager
from voice_broadcast import VoiceBroadcaster
from timer_manager import TimerManager
from card_listener import CardListener
from web_server import start_server, set_excel_manager, set_ngrok_url

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("signin")


def load_config(path="config.yaml"):
    if not os.path.exists(path):
        print(f"[错误] 配置文件不存在: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_settings():
    """加载 settings.json"""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def find_ngrok():
    """查找 ngrok 可执行文件路径"""
    # 常见路径
    candidates = [
        "ngrok",
        "/usr/local/bin/ngrok",
        os.path.expanduser("~/ngrok"),
        os.path.expanduser("~/Downloads/ngrok"),
    ]
    for c in candidates:
        try:
            result = subprocess.run([c, "version"], capture_output=True, timeout=5)
            if result.returncode == 0:
                return c
        except Exception:
            continue
    return None


def start_ngrok(port, auth_token=None):
    """启动 ngrok 隧道，返回公网 URL"""
    ngrok_path = find_ngrok()
    if not ngrok_path:
        logger.warning("未找到 ngrok，外网访问功能不可用。安装: brew install ngrok")
        return None

    try:
        # 如果提供了 auth token，先配置
        if auth_token:
            subprocess.run([ngrok_path, "config", "add-authtoken", auth_token],
                           capture_output=True, timeout=30)

        # 启动 ngrok
        proc = subprocess.Popen(
            [ngrok_path, "http", str(port), "--log=stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 等待 ngrok 启动并获取公网 URL
        deadline = time.time() + 15
        public_url = None

        while time.time() < deadline:
            line = proc.stdout.readline()
            if not line:
                time.sleep(0.2)
                continue
            # ngrok 日志中查找 URL
            if "url=" in line:
                import re
                match = re.search(r'url=([^\s]+)', line)
                if match:
                    public_url = match.group(1)
                    break
            # 新版 ngrok 格式
            if "started tunnel" in line.lower():
                import re
                match = re.search(r'(https://[^\s]+)', line)
                if match:
                    public_url = match.group(1)
                    break

        if public_url:
            logger.info(f"ngrok 隧道已建立，外网地址: {public_url}")
            set_ngrok_url(public_url)
            return public_url
        else:
            logger.warning("ngrok 启动但未能获取公网 URL")
            return None

    except Exception as e:
        logger.warning(f"ngrok 启动失败: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="身份证签到系统")
    parser.add_argument("--config", "-c", default="config.yaml",
                        help="配置文件路径 (默认: config.yaml)")
    parser.add_argument("--no-ngrok", action="store_true",
                        help="禁用 ngrok 外网隧道")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # 加载配置
    config = load_config(args.config)
    location = config.get("location", "默认地点")
    excel_dir = config.get("excel_dir", "./签到记录")
    voice_cfg = config.get("voice", {})
    timer_cfg = config.get("timer", {})
    web_cfg = config.get("web_server", {})
    card_cfg = config.get("card_reader", {})
    ngrok_cfg = config.get("ngrok", {})

    # 加载 settings.json (后台面板设置优先于 config.yaml)
    settings = load_settings()
    if settings.get("voice"):
        voice_cfg.update(settings["voice"])
    if settings.get("timer"):
        timer_cfg.update(settings["timer"])

    print("=" * 55)
    print("  身份证签到系统 v1.0")
    print(f"  签到地点: {location}")
    print(f"  数据目录: {excel_dir}")
    print(f"  管理后台: /admin")
    print("=" * 55)

    # ---- 初始化模块 ----
    excel_mgr = ExcelManager(excel_dir, location)
    logger.info(f"Excel 管理器已初始化")

    voice = VoiceBroadcaster(voice_cfg)
    voice.start()
    if voice_cfg.get("enabled", True):
        logger.info("语音播报已启用")
        voice.speak("签到系统已启动")

    remind_minutes = timer_cfg.get("remind_minutes", 40)
    timer_mgr = TimerManager(remind_minutes, voice)
    timer_mgr.start()
    logger.info(f"计时管理器已启动，提醒间隔: {remind_minutes} 分钟")

    def on_signin(name, id_number, raw_text):
        record = excel_mgr.add_record(name, id_number)
        voice.welcome(name)
        timer_mgr.add_timer(name, id_number)
        logger.info(f"新签到 — 序号:{record['seq']} 姓名:{name} 身份证:{id_number}")

    card_listener = CardListener(card_cfg, on_signin)
    card_listener.start()

    # ---- Web 服务器 ----
    set_excel_manager(excel_mgr)
    web_host = web_cfg.get("host", "0.0.0.0")
    web_port = web_cfg.get("port", 5002)
    start_server(host=web_host, port=web_port)

    # ---- ngrok 外网隧道 ----
    if not args.no_ngrok and ngrok_cfg.get("enabled", False):
        threading.Thread(
            target=lambda: start_ngrok(web_port, ngrok_cfg.get("auth_token")),
            daemon=True
        ).start()

    # ---- 主循环 ----
    print("\n系统运行中... 按 Ctrl+C 退出\n")

    shutdown_flag = [False]

    def handle_shutdown(signum, frame):
        if shutdown_flag[0]:
            return
        shutdown_flag[0] = True
        print("\n正在关闭系统...")
        card_listener.stop()
        voice.speak("签到系统已关闭")
        voice.stop()
        timer_mgr.stop()
        print("系统已安全退出")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        while not shutdown_flag[0]:
            time.sleep(1)
    except KeyboardInterrupt:
        handle_shutdown(None, None)


if __name__ == "__main__":
    main()
