"""
USB 身份证读卡器后台监听模块
- 全局键盘钩子（只读，不拦截，不影响原有系统）
- 通过击键间隔识别读卡器快速输入
- 正则提取姓名和身份证号
- 支持调试模式查看原始数据
"""

import re
import time
import threading
import logging

logger = logging.getLogger(__name__)

try:
    from pynput import keyboard
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False
    logger.warning("pynput 未安装，读卡器监听功能不可用")


class CardListener:
    """身份证读卡器数据监听器"""

    def __init__(self, config, on_signin):
        """
        config: card_reader 配置段
        on_signin: 回调函数 (name, id_number, raw_text) -> None
        """
        self.rapid_threshold = config.get("rapid_threshold", 0.03)
        self.pause_threshold = config.get("pause_threshold", 0.8)
        self.debug = config.get("debug", False)
        self.on_signin = on_signin

        # 正则模式
        self.id_re = re.compile(r'(\d{17}[\dXx])')      # 18位身份证号
        self.name_re = re.compile(r'[一-龥]{2,4}')  # 2-4字中文姓名
        # 常见标签（需要从姓名匹配结果中排除的）
        self.label_re = re.compile(
            r'(姓名|名字|性别|民族|出生|住址|地址|签发|有效期|'
            r'公民身份号码|身份证号|证件号码|号码|签发机关|'
            r'授权码|卡号|编号)'
        )

        # 内部状态
        self._buffer = []
        self._last_key_time = 0
        self._in_burst = False
        self._listener = None
        self._running = False

    def _log_debug(self, msg):
        if self.debug:
            print(f"[CardReader DEBUG] {msg}")

    # ---------- 键盘事件处理 ----------

    def _on_press(self, key):
        try:
            char = key.char
        except AttributeError:
            char = None

        now = time.time()

        if char is not None:
            interval = now - self._last_key_time if self._last_key_time > 0 else 1.0
            self._last_key_time = now

            if interval < self.rapid_threshold:
                # 极快速输入 — 很可能是读卡器
                if not self._in_burst:
                    self._in_burst = True
                    self._buffer = []
                    self._log_debug("检测到快速输入突发，开始缓存读卡器数据...")
                self._buffer.append(char)
            elif self._in_burst:
                if interval > self.pause_threshold:
                    # 突发结束，处理数据
                    self._log_debug(f"突发结束，缓存长度: {len(self._buffer)}")
                    self._process_buffer()
                    self._in_burst = False
                    self._buffer = []
                    # 当前字符可能是一次新的正常输入，忽略
                else:
                    # 仍在突发中，继续缓存
                    self._buffer.append(char)
        else:
            # 特殊按键（回车、Tab等）在读卡数据中常作为分隔符
            if self._in_burst:
                # 记录为分隔符，继续等待数据结束
                self._buffer.append('\n')

    # ---------- 数据解析 ----------

    def _process_buffer(self):
        """解析缓存的按键数据，提取姓名和身份证号"""
        if not self._buffer:
            return

        text = ''.join(self._buffer).strip()
        if not text:
            return

        self._log_debug(f"原始数据: {repr(text)}")

        # 查找身份证号（最可靠的标识）
        id_match = self.id_re.search(text)
        if not id_match:
            self._log_debug("未检测到身份证号，忽略（可能为正常打字）")
            return

        id_number = id_match.group(1).upper()

        # 查找中文姓名
        name = self._extract_name(text)

        # 如果没找到姓名但找到了身份证号，至少有身份证号
        if not name:
            name = "未知"

        self._log_debug(f"解析结果: 姓名={name}, 身份证号={id_number}")

        # 通知回调
        try:
            self.on_signin(name, id_number, text)
        except Exception as e:
            logger.error(f"签到回调异常: {e}")

    def _extract_name(self, text):
        """从文本中提取中文姓名"""
        # 去掉换行符，规范化空格
        cleaned = text.replace('\n', ' ').replace('\r', ' ')

        # 找到所有中文姓名候选项
        candidates = self.name_re.findall(cleaned)

        for cand in candidates:
            # 跳过标签词
            if self.label_re.match(cand):
                continue
            # 跳过不常见的姓名用字组合
            return cand

        return ""

    # ---------- 生命周期 ----------

    def start(self):
        """启动键盘监听"""
        if not HAS_PYNPUT:
            print("[错误] pynput 未安装，无法启动读卡器监听。请运行: pip install pynput")
            return

        self._running = True
        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.start()
        print("[读卡器监听] 已启动，等待刷卡...")
        if self.debug:
            print("[读卡器监听] 调试模式已开启，将显示原始刷卡数据")

    def stop(self):
        """停止键盘监听"""
        self._running = False
        if self._listener:
            self._listener.stop()
