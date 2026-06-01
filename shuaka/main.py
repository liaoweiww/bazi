#!/usr/bin/env python3
"""
身份证签到系统 — 主程序入口（跨平台：macOS / Windows）
- 后台监听 USB 身份证读卡器（macOS: pynput 键盘钩子 / Windows: 底层 WH_KEYBOARD_LL）
- 自动生成 Excel 签到记录
- 离线语音播报 + 超时提醒
- 本地 Web 服务器 + 管理后台 (/admin)
- 支持 ngrok 内网穿透实现外网访问
- 百度网盘跨端数据同步

启动方式：
    python main.py
    python main.py --config /path/to/config.yaml
"""

import os
import sys
import re
import json
import time
import signal
import argparse
import logging
import subprocess
import threading
import ctypes

import yaml

# Windows Raw Input 不需要管理员权限，直接运行即可

from excel_manager import ExcelManager
from voice_broadcast import VoiceBroadcaster
from timer_manager import TimerManager
from web_server import start_server, set_excel_manager, set_ngrok_url, set_monitor_card_online, set_monitor_card_read, set_monitor_started, set_card_reader_enabled, set_voice_broadcaster, set_timer_manager, _write_event
from platform_utils import IS_WIN, IS_MAC, IS_LINUX, SYSTEM, print_env, get_ngrok_path, get_baidu_sync_dir, get_sync_data_dir
from auth_manager import is_activated, get_machine_code
from local_mirror import mirror_critical_data, ensure_dirs, restore_from_local

# 平台适配：导入对应系统的读卡监听器
if IS_WIN:
    CardListener = None
    from win_card_listener import WinCardListener as CardListener
    try:
        from win_com_reader import ComCardReader
    except ImportError:
        ComCardReader = None
    print("[加载] 尝试导入鱼住读卡器...")
    try:
        from yz_card_reader import YzCardReader
        print(f"[加载] 鱼住读卡器导入成功 YzCardReader={YzCardReader}")
    except Exception as _e2:
        print(f"[加载] 鱼住读卡器导入失败: {_e2}")
        YzCardReader = None

    # ====== 内嵌全窗口扫描读卡器 ======
    _ID_RE = re.compile(r'(\d{17}[\dXx])')
    _NAME_RE = re.compile(r'[一-鿿]{2,4}')
    _BAD = {"姓名","性别","民族","出生","住址","签发","有效期","号码","机关","读卡","离线","在线","检测","请插入","Microsoft","Windows","Program","Default","确定","取消","关闭","设置","测试","帮助","MSCTF","GDI","IME","开始","任务栏","----","-->","Button","Static"}

    class _WindowReader:
        def __init__(self, config=None, on_signin=None):
            self.on_signin = on_signin; self._seen = set(); self._running = False
        def _log(self, msg): print(f"[全窗扫描] {msg}")

        def _scan(self):
            u32 = ctypes.windll.user32
            texts = []
            h = u32.GetTopWindow(None)
            while h:
                if u32.IsWindowVisible(h):
                    for sz in [256, 512]:
                        cb = ctypes.create_unicode_buffer(sz)
                        u32.GetWindowTextW(h, cb, sz)
                        if cb.value:
                            t = cb.value.strip()
                            if t and len(t) >= 2 and t not in self._BAD:
                                cc = ctypes.create_unicode_buffer(128)
                                u32.GetClassNameW(h, cc, 128)
                                texts.append(f"{cc.value}:{t}")
                            break
                    # 子窗口
                    ch = u32.FindWindowExW(h, None, None, None)
                    while ch:
                        if u32.IsWindowVisible(ch):
                            for sz in [256, 512]:
                                cb2 = ctypes.create_unicode_buffer(sz)
                                u32.GetWindowTextW(ch, cb2, sz)
                                if cb2.value:
                                    t2 = cb2.value.strip()
                                    if t2 and len(t2) >= 2 and t2 not in self._BAD:
                                        cc2 = ctypes.create_unicode_buffer(128)
                                        u32.GetClassNameW(ch, cc2, 128)
                                        texts.append(f"{cc2.value}:{t2}")
                                    break
                        ch = u32.FindWindowExW(h, ch, None, None)
                h = u32.GetWindow(h, 2)
            return texts

        def _loop(self):
            self._log("启动")
            last = ""; count = 0
            while self._running:
                try:
                    texts = self._scan()
                    text = " ".join(texts)
                    count += 1
                    if count <= 2 or text != last:
                        # 只显示含中文的窗口
                        cn = [t for t in texts if any('一' <= c <= '鿿' for c in t)]
                        self._log(f"扫描{count}: {len(texts)}窗 {len(cn)}中文" + (f" | {' | '.join(cn[:15])}" if cn else ""))
                    if text != last and text:
                        last = text
                        ids = set(self._ID_RE.findall(text))
                        new = ids - self._seen
                        if new:
                            self._seen |= ids
                            m = self._ID_RE.search(text)
                            if m:
                                idn = m.group(1).upper()
                                nm = ""
                                for mx in self._NAME_RE.finditer(text):
                                    n = mx.group()
                                    if n not in self._BAD and len(n) >= 2: nm = n; break
                                self._log(f">>> 抓到: {nm or '未知'} {idn}")
                                if self.on_signin:
                                    self.on_signin(nm or "未知", idn, text, {})
                except Exception as _e:
                    if count <= 3: self._log(f"异常: {_e}")
                time.sleep(2)

        def start(self):
            self._running = True
            threading.Thread(target=self._loop, daemon=True).start()
            self._log("已启动")
        def stop(self): self._running = False

    WindowCardReader = _WindowReader
else:
    try:
        from card_listener import CardListener
    except ImportError:
        CardListener = None
    ComCardReader = None
    WindowCardReader = None

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


def _get_machine_json_path():
    """本机专属配置文件路径（不参与 SMB/云同步）"""
    import platform
    if platform.system() == 'Windows':
        local_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'shuaka')
    else:
        local_dir = os.path.join(os.path.expanduser('~'), '.shuaka')
    os.makedirs(local_dir, exist_ok=True)
    return os.path.join(local_dir, 'machine.json')

def load_settings():
    """加载 settings.json（优先百度云同步目录）+ 本机 machine.json 覆盖"""
    result = {}
    sync_dir = get_sync_data_dir()
    if sync_dir:
        sync_path = os.path.join(sync_dir, "settings.json")
        if os.path.exists(sync_path):
            with open(sync_path, "r", encoding="utf-8") as f:
                result = json.load(f)
    if not result:
        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        if os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                result = json.load(f)
    # 合并本机专属配置（machine.json 中的值优先）
    machine_path = _get_machine_json_path()
    if os.path.exists(machine_path):
        with open(machine_path, "r", encoding="utf-8") as f:
            machine = json.load(f)
        for k in machine:
            if k in result and isinstance(result[k], dict) and isinstance(machine[k], dict):
                result[k] = {**result[k], **machine[k]}
            else:
                result[k] = machine[k]
    return result


def find_ngrok():
    """查找 ngrok 可执行文件路径（使用平台通用查找）"""
    return get_ngrok_path()


def start_ngrok(port, auth_token=None):
    """启动 ngrok 隧道，返回公网 URL"""
    ngrok_path = find_ngrok()
    if not ngrok_path:
        logger.warning("未找到 ngrok，外网访问功能不可用。" +
                       ("安装: winget install ngrok" if IS_WIN else "安装: brew install ngrok"))
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
    excel_dir = config.get("excel_dir") or "./签到记录"
    voice_cfg = config.get("voice", {})
    timer_cfg = config.get("timer", {})
    web_cfg = config.get("web_server", {})
    card_cfg = config.get("card_reader", {})
    ngrok_cfg = config.get("ngrok", {})

    # 百度网盘同步：优先使用同步目录存放数据（多机共享）
    sync_dir = get_sync_data_dir(base_dir=script_dir)
    if sync_dir:
        excel_dir = os.path.join(sync_dir, "签到记录")
        # 自动迁移旧数据到 tongbu/ 目录（仅首次）
        old_items = {
            "签到记录": True, "备份": True, "回收站": True, "uploads": True,
        }
        old_files = ["settings.json", "users.json"]
        for name, is_dir in old_items.items():
            old_path = os.path.join(script_dir, name)
            new_path = os.path.join(sync_dir, name)
            if os.path.isdir(old_path):
                os.makedirs(new_path, exist_ok=True)
                for fn in os.listdir(old_path):
                    sf, df = os.path.join(old_path, fn), os.path.join(new_path, fn)
                    if os.path.isfile(sf) and not os.path.exists(df):
                        import shutil as _shutil
                        _shutil.copy2(sf, df)
                        print(f"[迁移] {name}/{fn}")
        for fn in old_files:
            old_f = os.path.join(script_dir, fn)
            new_f = os.path.join(sync_dir, fn)
            if os.path.isfile(old_f) and not os.path.isfile(new_f):
                import shutil as _shutil
                _shutil.copy2(old_f, new_f)
                print(f"[迁移] {fn}")
        print(f"[数据同步] 数据将自动同步到百度云")

    # 加载 settings.json (后台面板设置优先于 config.yaml)
    settings = load_settings()
    if settings.get("data_path"):
        custom = settings["data_path"]
        if os.path.exists(custom):
            excel_dir = custom
        elif os.path.isdir(os.path.dirname(custom)):
            excel_dir = custom
        else:
            print(f"[警告] 自定义数据路径无效，已忽略: {custom}")
    if settings.get("voice"):
        voice_cfg.update(settings["voice"])
    if settings.get("timer"):
        timer_cfg.update(settings["timer"])

    print("=" * 55)
    print("  身份证签到系统 v1.0")
    print(f"  签到地点: {location}")
    print(f"  数据目录: {excel_dir}")
    print(f"  数据同步: {'百度网盘 ✓' if sync_dir else '仅本机'}")
    print(f"  管理后台: /admin")
    print(f"  运行平台: {SYSTEM}")
    activated = is_activated()
    print(f"  激活状态: {'已激活 ✓' if activated else '未激活 ✗  请访问 /activate 输入授权码'}")
    import datetime
    print(f"  代码更新: {datetime.datetime.fromtimestamp(os.path.getmtime(__file__)).strftime('%H:%M:%S')}")
    print("=" * 55)

    # ---- 初始化模块 ----
    excel_mgr = ExcelManager(excel_dir, location)
    logger.info(f"Excel 管理器已初始化")
    ensure_dirs()           # 确保所有数据目录存在
    restore_from_local()    # BaiduSyncdisk 数据缺失时从本地备份恢复
    mirror_critical_data()  # 启动时全量镜像到本地

    voice = VoiceBroadcaster(voice_cfg)
    voice.start()
    if voice_cfg.get("enabled", True):
        logger.info("语音播报已启用")
        st_tpl = voice_cfg.get("templates", {}).get("startup", "签到系统已启动")
        voice.speak(st_tpl)

    remind_minutes = timer_cfg.get("remind_minutes", 40)
    timer_mgr = TimerManager(remind_minutes, voice)
    timer_mgr.start()
    logger.info(f"计时管理器已启动，提醒间隔: {remind_minutes} 分钟")

    def on_signin(name, id_number, raw_text, extra_data=None):
        record = excel_mgr.add_record(name, id_number)
        voice.welcome(name)
        timer_mgr.add_timer(name, id_number)
        logger.info(f"新签到 — 序号:{record['seq']} 姓名:{name} 身份证:{id_number}")
        set_monitor_card_read(name, id_number)
        welcome_tpl = voice_cfg.get("welcome_template", "{name}，欢迎签到！")
        welcome_text = welcome_tpl.replace("{name}", name)
        _write_event("signin", name=name, text=welcome_text)

    # 读卡器监听（仅 card_reader.enabled=true 的机器启动）
    card_listener = None
    card_cfg_merged = dict(card_cfg)
    if settings.get("card_reader"):
        card_cfg_merged.update(settings["card_reader"])
    card_enabled = card_cfg_merged.get("enabled", False)
    set_card_reader_enabled(card_enabled)
    if not card_enabled:
        logger.info("读卡器未启用（card_reader.enabled=false），本机作为同步终端运行")
    else:
        # 自动选择读卡模式：优先窗口抓取 → COM口 → 键盘钩子
        card_listener = None
        started = False

        def _try_start(name, listener_cls):
            nonlocal started, card_listener
            print(f"[启动] 尝试 {name}: started={started} cls={'None' if listener_cls is None else 'OK'}")
            if started or listener_cls is None:
                return False
            try:
                card_listener = listener_cls(card_cfg_merged, on_signin)
                card_listener.start()
                set_monitor_card_online(True)
                started = True
                logger.info(f"{name}已启动")
                return True
            except Exception as e:
                logger.info(f"{name}不可用: {e}")
                return False

        if IS_WIN:
            _try_start("鱼住读卡", YzCardReader) or \
            _try_start("键盘钩子读卡", CardListener) or \
            _try_start("COM口读卡", ComCardReader) or \
            _try_start("窗口读卡", WindowCardReader)
        else:
            _try_start("读卡器监听", CardListener)

        if not started:
            logger.warning("无可用的读卡模式，仅支持手动签到")

    # ---- Web 服务器 ----
    set_excel_manager(excel_mgr)
    set_voice_broadcaster(voice)
    set_timer_manager(timer_mgr)
    set_monitor_started()
    web_host = web_cfg.get("host", "0.0.0.0")
    web_port = web_cfg.get("port", 5002)
    start_server(host=web_host, port=web_port)

    # ---- ngrok 外网隧道 ----
    if not args.no_ngrok and ngrok_cfg.get("enabled", False):
        threading.Thread(
            target=lambda: start_ngrok(web_port, ngrok_cfg.get("auth_token")),
            daemon=True
        ).start()

    # ---- 关闭标志 ----
    shutdown_flag = [False]

    # ---- 自动备份 ----
    backup_interval = config.get("backup", {}).get("interval_minutes", 30)
    backup_enabled = config.get("backup", {}).get("enabled", True)

    def auto_backup_loop():
        import shutil, glob as _glob
        while not shutdown_flag[0]:
            time.sleep(backup_interval * 60)
            if shutdown_flag[0]:
                break
            try:
                now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = config.get("backup", {}).get("path") or (os.path.join(sync_dir, "备份") if sync_dir else os.path.join(script_dir, "备份"))
                os.makedirs(backup_dir, exist_ok=True)
                excel_dir = excel_mgr.excel_dir
                for f in _glob.glob(os.path.join(excel_dir, "签到记录_*.xlsx")):
                    bn = os.path.basename(f)
                    shutil.copy2(f, os.path.join(backup_dir, f"{now_str}_自动_{bn}"))
                # 清理旧备份（保留最近50份）
                all_baks = sorted(_glob.glob(os.path.join(backup_dir, "*_自动_*")))
                while len(all_baks) > 50:
                    try: os.remove(all_baks.pop(0))
                    except: pass
                logger.info(f"自动备份完成 ({backup_interval}分钟)")
            except Exception as e:
                logger.warning(f"自动备份失败: {e}")

    if backup_enabled:
        threading.Thread(target=auto_backup_loop, daemon=True).start()
        logger.info(f"自动备份已启用，间隔: {backup_interval} 分钟")

    # ---- 主循环 ----
    print("\n系统运行中... 按 Ctrl+C 退出\n")

    def handle_shutdown(signum, frame):
        if shutdown_flag[0]:
            return
        shutdown_flag[0] = True
        print("\n正在关闭系统...")
        if card_listener: card_listener.stop()
        sd_tpl = voice_cfg.get("templates", {}).get("shutdown", "签到系统已关闭")
        voice.speak(sd_tpl)
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
