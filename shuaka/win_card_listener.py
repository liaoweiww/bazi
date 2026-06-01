"""
Windows USB 身份证读卡器 — 原始数据流监听模块

原理：
  - USB 身份证读卡器在刷卡瞬间向系统发送原生明文数据
  - 通过 Windows 底层键盘钩子 (WH_KEYBOARD_LL) 捕获击键流
  - 利用刷卡数据的"极速输入"特征（<50ms/键）区分人工打字
  - 解析提取姓名、性别、民族、出生日期、住址、身份证号等全字段

全程不依赖任何第三方读卡软件，直接读取设备原始输出。
"""

import re
import time
import threading
import logging
import sys
import ctypes
from ctypes import wintypes, POINTER, CFUNCTYPE, cast, c_int, c_void_p

logger = logging.getLogger(__name__)

# ========== Windows API 常量与结构体 ==========

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104

# 用户32 DLL
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# 钩子回调类型
HOOKPROC = CFUNCTYPE(ctypes.c_long, c_int, wintypes.WPARAM, wintypes.LPARAM)

# KBDLLHOOKSTRUCT 结构体
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

# SetWindowsHookEx 函数指针
SetWindowsHookExW = user32.SetWindowsHookExW
SetWindowsHookExW.argtypes = [c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
SetWindowsHookExW.restype = wintypes.HHOOK

CallNextHookEx = user32.CallNextHookEx
CallNextHookEx.argtypes = [wintypes.HHOOK, c_int, wintypes.WPARAM, wintypes.LPARAM]
CallNextHookEx.restype = ctypes.c_long

UnhookWindowsHookEx = user32.UnhookWindowsHookEx
UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
UnhookWindowsHookEx.restype = wintypes.BOOL

GetMessageW = user32.GetMessageW
GetMessageW.argtypes = [POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
GetMessageW.restype = wintypes.BOOL

# MSG 结构体
class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt_x", wintypes.LONG),
        ("pt_y", wintypes.LONG),
    ]

# 虚拟键码 → 字符映射
_vk_map = {}
for _code in range(32, 127):
    _vk_map[_code] = chr(_code)

# 数字行 VK → 字符 (shift off / shift on)
_VK_SHIFT_MAP = {
    0x30: ('0', ')'), 0x31: ('1', '!'), 0x32: ('2', '@'), 0x33: ('3', '#'),
    0x34: ('4', '$'), 0x35: ('5', '%'), 0x36: ('6', '^'), 0x37: ('7', '&'),
    0x38: ('8', '*'), 0x39: ('9', '('),
    0xBA: (';', ':'), 0xBB: ('=', '+'), 0xBC: (',', '<'),
    0xBD: ('-', '_'), 0xBE: ('.', '>'), 0xBF: ('/', '?'),
    0xDB: ('[', '{'), 0xDC: ('\\', '|'), 0xDD: (']', '}'), 0xDE: ("'", '"'),
}


class WinCardListener:
    """
    Windows 身份证读卡器监听器

    用法:
        def on_card(read_data):
            print(read_data["name"], read_data["id_number"])

        listener = WinCardListener(on_card)
        listener.start()
    """

    def __init__(self, config=None, on_signin=None):
        """
        config: dict, card_reader 配置段
        on_signin: callback(name, id_number, raw_text, extra_fields)
        """
        config = config or {}
        self.rapid_threshold = config.get("rapid_threshold", 0.05)   # 50ms
        self.pause_threshold = config.get("pause_threshold", 0.5)    # 500ms
        self.debug = config.get("debug", False)
        self.on_signin = on_signin

        # ----- 正则模式 -----
        self.id_re = re.compile(r'(\d{17}[\dXx])')                    # 18位身份证号
        self.name_re = re.compile(r'[一-鿿]{2,4}')            # 2-4字中文姓名
        self.gender_re = re.compile(r'[男女]')                        # 性别
        self.ethnicity_re = re.compile(r'[一-龥]{1,3}族?')           # 民族
        self.birth_re = re.compile(r'(\d{4})[年\-./]?(\d{1,2})[月\-./]?(\d{1,2})')  # 出生日期
        self.address_re = re.compile(r'[一-鿿]{4,}[一-鿿\d\-\.（）()]*')  # 住址

        # 常见标签词（需排除的姓名候选）
        self.label_words = re.compile(
            r'(姓名|名字|性别|民族|出生|住址|地址|签发|有效期|'
            r'公民身份号码|身份证号|证件号码|号码|签发机关|授权码|卡号|编号)'
        )

        # ----- 内部状态 -----
        self._buffer = []
        self._last_key_time = 0
        self._in_burst = False
        self._hook_id = None
        self._running = False
        self._hook_proc = None
        self._msg_thread = None

    def _log(self, msg):
        if self.debug:
            print(f"[CardReader] {msg}")

    # ---------- 键盘钩子 ----------

    def _keyboard_proc(self, nCode, wParam, lParam):
        """WH_KEYBOARD_LL 回调"""
        if nCode >= 0:
            if wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
                kbd = cast(lParam, POINTER(KBDLLHOOKSTRUCT)).contents
                self._handle_key(kbd.vkCode)
        return CallNextHookEx(self._hook_id, nCode, wParam, lParam)

    def _handle_key(self, vk_code):
        """处理单个按键"""
        now = time.time()

        # 虚拟键 → 字符
        char = self._vk_to_char(vk_code)
        if char is None:
            return

        interval = now - self._last_key_time if self._last_key_time > 0 else 1.0
        self._last_key_time = now

        if interval < self.rapid_threshold:
            # 极速输入 — 读卡器特征
            if not self._in_burst:
                self._in_burst = True
                self._buffer = []
                self._log("检测到快速输入突发，缓存读卡器数据...")
            self._buffer.append(char)
        elif self._in_burst:
            if interval > self.pause_threshold:
                # 突发结束
                self._log(f"突发结束，缓存长度: {len(self._buffer)}")
                self._process_buffer()
                self._in_burst = False
                self._buffer = []
            else:
                self._buffer.append(char)

    def _vk_to_char(self, vk_code):
        """虚拟键码 → 可打印字符"""
        # 特殊键
        if vk_code == 0x0D:     # Enter
            return '\n'
        if vk_code == 0x20:     # Space
            return ' '
        if vk_code == 0x09:     # Tab
            return '\t'

        # 标准 ASCII
        if 0x30 <= vk_code <= 0x5A:
            return chr(vk_code)

        # 扩展键
        if vk_code in _VK_SHIFT_MAP:
            return _VK_SHIFT_MAP[vk_code][0]

        return None

    # ---------- 数据解析 ----------

    def _process_buffer(self):
        """解析缓存数据，提取身份证全字段"""
        if not self._buffer:
            return

        text = ''.join(self._buffer).strip()
        if not text:
            return

        self._log(f"原始数据: {repr(text[:200])}")

        # 1. 找身份证号（最可靠标识）
        id_match = self.id_re.search(text)
        if not id_match:
            self._log("未检测到身份证号，忽略")
            return

        id_number = id_match.group(1).upper()

        # 2. 验证校验位
        if not self._validate_id_checksum(id_number):
            self._log(f"身份证校验位不合法: {id_number}")
            return

        # 3. 提取各字段
        result = self._extract_fields(text, id_number)

        name = result.get("name", "未知")
        self._log(f"解析结果: 姓名={name} 身份证号={id_number} 性别={result.get('gender','')}")

        # 4. 通知回调
        if self.on_signin:
            try:
                self.on_signin(name, id_number, text, result)
            except Exception as e:
                logger.error(f"签到回调异常: {e}")

    def _extract_fields(self, text, id_number):
        """从原始文本中提取所有身份证字段"""
        fields = {
            "name": "",
            "gender": "",
            "ethnicity": "",
            "birth_date": "",
            "address": "",
            "id_number": id_number,
            "issuing_authority": "",
            "expiry_date": "",
        }

        # 标准化文本（统一换行和空格）
        cleaned = text.replace('\n', ' ').replace('\r', ' ')

        # --- 姓名 ---
        for cand in self.name_re.findall(cleaned):
            if not self.label_words.match(cand):
                fields["name"] = cand
                break

        # --- 性别：优先从身份证号第17位推导 ---
        try:
            gender_digit = int(id_number[16])
            fields["gender"] = "男" if gender_digit % 2 == 1 else "女"
        except (IndexError, ValueError):
            gm = self.gender_re.search(cleaned)
            if gm:
                fields["gender"] = gm.group()

        # --- 出生日期：优先从身份证号第7-14位推导 ---
        try:
            b = id_number[6:14]
            fields["birth_date"] = f"{b[0:4]}-{b[4:6]}-{b[6:8]}"
        except IndexError:
            bm = self.birth_re.search(cleaned)
            if bm:
                y, m, d = bm.groups()
                fields["birth_date"] = f"{y}-{m.zfill(2)}-{d.zfill(2)}"

        # --- 住址 ---
        addr_start = -1
        addr_matches = list(self.address_re.finditer(cleaned))
        for m in addr_matches:
            s = m.group()
            if len(s) > len(fields["address"]):
                # 排除身份证号自身
                if s != id_number:
                    fields["address"] = s

        # --- 签发机关 ---
        auth_match = re.search(r'签发机关[:：]?\s*([^\n\r]{4,})', text)
        if auth_match:
            fields["issuing_authority"] = auth_match.group(1).strip()

        # --- 有效期 ---
        expiry_match = re.search(
            r'有效期[:：]?\s*(\d{4}[./-]\d{1,2}[./-]\d{1,2})\s*[-~至到]\s*(\d{4}[./-]\d{1,2}[./-]\d{1,2}|长期)',
            text
        )
        if expiry_match:
            fields["expiry_date"] = f"{expiry_match.group(1)}-{expiry_match.group(2)}"

        return fields

    # ---------- 身份证校验 ----------

    @staticmethod
    def _validate_id_checksum(id_number):
        """验证 18 位身份证校验位"""
        if len(id_number) != 18:
            return True  # 非标长度，跳过校验

        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = "10X98765432"

        try:
            digits = [int(c) for c in id_number[:17]]
            total = sum(w * d for w, d in zip(weights, digits))
            expected = check_codes[total % 11]
            return id_number[17].upper() == expected
        except (ValueError, IndexError):
            return True  # 解析失败不阻断

    # ---------- 生命周期 ----------

    def start(self):
        """启动键盘钩子监听"""
        self._running = True

        # 保存回调引用防 GC
        self._hook_proc = HOOKPROC(self._keyboard_proc)

        # 安装底层键盘钩子（PyInstaller 下 hMod=None 更可靠）
        hmod = kernel32.GetModuleHandleW(None)
        self._hook_id = SetWindowsHookExW(WH_KEYBOARD_LL, self._hook_proc, hmod, 0)
        if not self._hook_id:
            # 重试：部分环境需 hMod=NULL
            self._hook_id = SetWindowsHookExW(WH_KEYBOARD_LL, self._hook_proc, 0, 0)

        if not self._hook_id:
            raise OSError("无法安装键盘钩子（需要管理员权限或 Python 以管理员身份运行）")

        # 消息循环线程（钩子需要消息泵）
        self._msg_thread = threading.Thread(target=self._message_loop, daemon=True)
        self._msg_thread.start()

        print("[读卡器监听] Windows 底层键盘钩子已启动，等待刷卡...")
        if self.debug:
            print("[读卡器监听] 调试模式已开启，将显示原始刷卡数据")

    def _message_loop(self):
        """Windows 消息循环（钩子必需）"""
        msg = MSG()
        while self._running:
            try:
                GetMessageW(ctypes.byref(msg), None, 0, 0)
            except Exception:
                break

    def stop(self):
        """停止监听"""
        self._running = False
        if self._hook_id:
            UnhookWindowsHookEx(self._hook_id)
            self._hook_id = None
        print("[读卡器监听] 已停止")

