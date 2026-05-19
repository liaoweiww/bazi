"""
离线语音播报模块
- macOS: 调用系统内置 say 命令 (支持中文 Tingting 语音)
- Windows: 使用 pyttsx3 (SAPI5)
- 队列式播报，避免语音重叠
"""

import subprocess
import sys
import threading
import queue


class VoiceBroadcaster:
    def __init__(self, config):
        self.enabled = config.get("enabled", True)
        self.macos_voice = config.get("macos_voice", "Tingting")
        self.windows_voice = config.get("windows_voice", "")
        self.welcome_template = config.get("welcome_template", "{name}，欢迎签到！")
        self.remind_template = config.get("remind_template",
                                          "{name}，您的等待时间已到，请留意叫号。")

        self._queue = queue.Queue()
        self._worker_thread = None
        self._running = False
        self._engine = None

        self._init_engine()

    def _init_engine(self):
        """初始化语音引擎"""
        if sys.platform == "darwin":
            # macOS: 使用内置 say 命令，无需额外初始化
            pass
        elif sys.platform == "win32":
            try:
                import pyttsx3
                self._engine = pyttsx3.init()
                if self.windows_voice:
                    voices = self._engine.getProperty('voices')
                    for v in voices:
                        if self.windows_voice in v.name:
                            self._engine.setProperty('voice', v.id)
                            break
                self._engine.setProperty('rate', 180)
            except Exception:
                self._engine = None
        else:
            # Linux: 尝试 espeak
            pass

    def start(self):
        if not self.enabled:
            return
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()

    def stop(self):
        self._running = False
        # 放入哨兵值让工作线程退出
        self._queue.put(None)

    def speak(self, text):
        """将文本加入播报队列"""
        if self.enabled and text:
            self._queue.put(text)

    def welcome(self, name):
        """播报欢迎签到"""
        text = self.welcome_template.format(name=name)
        self.speak(text)

    def remind(self, name):
        """播报40分钟提醒"""
        text = self.remind_template.format(name=name)
        self.speak(text)

    def _worker(self):
        """后台播报工作线程"""
        while self._running:
            try:
                text = self._queue.get(timeout=1)
            except queue.Empty:
                continue

            if text is None:  # 哨兵
                break

            self._speak_now(text)
            self._queue.task_done()

    def _speak_now(self, text):
        """实际执行语音播报"""
        try:
            if sys.platform == "darwin":
                subprocess.run(
                    ["say", "-v", self.macos_voice, text],
                    timeout=30
                )
            elif sys.platform == "win32":
                if self._engine:
                    self._engine.say(text)
                    self._engine.runAndWait()
                else:
                    # 回退到 import 再试一次
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.say(text)
                    engine.runAndWait()
            else:
                # Linux fallback
                try:
                    subprocess.run(["espeak", "-v", "zh", text], timeout=30)
                except FileNotFoundError:
                    pass  # espeak 未安装，静默跳过
        except Exception:
            pass  # 播报失败不影响主流程
