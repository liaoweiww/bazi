"""
离线语音播报模块
- macOS: 调用系统内置 say 命令 (支持中文语音)
- Windows: 使用 pyttsx3 (SAPI5)，每次播报独立线程避免 COM 持久化问题
- 队列式播报，避免语音重叠
"""

import subprocess
import sys
import threading
import time


class VoiceBroadcaster:
    def __init__(self, config):
        self.enabled = config.get("enabled", True)
        self.macos_voice = config.get("macos_voice", "Eddy")
        self.windows_voice = config.get("windows_voice", "")
        self.welcome_template = config.get("welcome_template", "{name}，欢迎签到！")
        self.remind_template = config.get("remind_template",
                                          "{name}，您的等待时间已到，请留意叫号。")

        self._lock = threading.Lock()       # 防重叠播报
        self._running = False

    def start(self):
        if not self.enabled:
            print("[语音] 已禁用")
            return
        self._running = True
        print("[语音] 播报已就绪")

    def stop(self):
        self._running = False

    def update_config(self, config):
        """动态更新语音配置（无需重启服务）"""
        if "welcome_template" in config:
            self.welcome_template = config["welcome_template"]
            print(f"[语音] 欢迎模板已更新: {self.welcome_template}")
        if "remind_template" in config:
            self.remind_template = config["remind_template"]
            print(f"[语音] 提醒模板已更新: {self.remind_template}")
        if "enabled" in config:
            self.enabled = config["enabled"]
        if "macos_voice" in config:
            self.macos_voice = config["macos_voice"]
        if "windows_voice" in config:
            self.windows_voice = config["windows_voice"]

    def speak(self, text):
        """将文本加入播报（独立线程，不依赖持久化 worker）"""
        if self._running and text:
            print(f"[语音] 入队: {text}")
            threading.Thread(target=self._speak_safe, args=(text,), daemon=True).start()
        else:
            print(f"[语音] 跳过: running={self._running} text={bool(text)}")

    def welcome(self, name):
        text = self.welcome_template.replace("{name}", name)
        self.speak(text)

    def remind(self, name):
        text = self.remind_template.replace("{name}", name)
        self.speak(text)

    # ========== 实际播报 ==========

    def _speak_safe(self, text):
        """带锁的播报，防止重叠"""
        with self._lock:
            self._speak_now(text)

    def _speak_now(self, text):
        """执行语音播报（在工作线程中运行，COM 安全）"""
        print(f"[语音] 播报: {text}")
        try:
            if sys.platform == "darwin":
                subprocess.run(["say", "-v", self.macos_voice, text], timeout=30)
            elif sys.platform == "win32":
                self._speak_win32(text)
            else:
                try:
                    subprocess.run(["espeak", "-v", "zh", text], timeout=30)
                except FileNotFoundError:
                    pass
        except Exception as e:
            print(f"[语音] 播报异常: {e}")

    def _speak_win32(self, text):
        """Windows 语音播报（每次独立初始化引擎，COM 线程安全）"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            if self.windows_voice:
                voices = engine.getProperty('voices')
                for v in voices:
                    if self.windows_voice in v.name:
                        engine.setProperty('voice', v.id)
                        break
            engine.setProperty('rate', 180)
            engine.say(text)
            engine.runAndWait()
            print(f"[语音] Windows 播报完成: {text}")
        except Exception as e:
            print(f"[语音] Windows 播报失败: {e}")
