"""
Windows COM口身份证读卡器 — 全自动检测 + 主动查询
自动扫描串口、自动匹配协议、无需任何手动配置
"""
import re
import time
import threading
import logging

logger = logging.getLogger(__name__)


class ComCardReader:
    def __init__(self, config=None, on_signin=None):
        config = config or {}
        self.debug = config.get("debug", True)
        self.on_signin = on_signin
        self._running = False
        self._serial = None

        self.id_re = re.compile(r'(\d{17}[\dXx])')
        self.name_re = re.compile(r'[一-鿿]{2,4}')

    def _log(self, msg):
        if self.debug:
            print(f"[COM读卡器] {msg}")

    @staticmethod
    def _list_ports():
        import serial.tools.list_ports
        return [(p.device, p.description) for p in serial.tools.list_ports.comports()]

    def _try_parse(self, text):
        id_match = self.id_re.search(text)
        if not id_match:
            return None
        id_number = id_match.group(1).upper()
        if not self._validate_checksum(id_number):
            return None
        name = "未知"
        for m in self.name_re.finditer(text):
            name = m.group()
            break
        return {"name": name, "id_number": id_number}

    @staticmethod
    def _validate_checksum(id_number):
        if len(id_number) != 18:
            return True
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = "10X98765432"
        try:
            digits = [int(c) for c in id_number[:17]]
            total = sum(w * d for w, d in zip(weights, digits))
            return id_number[17].upper() == check_codes[total % 11]
        except (ValueError, IndexError):
            return True

    def _decode(self, raw_bytes):
        """尝试多种编码解析原始数据"""
        for enc in ["gbk", "gb18030", "gb2312", "utf-16-le", "utf-8"]:
            try:
                text = raw_bytes.decode(enc, errors="ignore")
                if any('一' <= c <= '鿿' for c in text):
                    self._log(f"编码 {enc}: {text[:200]}")
                    return self._try_parse(text)
            except Exception:
                continue
        # ASCII 清洗
        import re as _re
        text = raw_bytes.decode("ascii", errors="ignore")
        text = _re.sub(r'[^\x20-\x7e一-鿿]', '', text)
        if text.strip():
            self._log(f"ASCII清洗: {text[:200]}")
            return self._try_parse(text)
        return None

    def _read_loop(self):
        import serial
        while self._running:
            try:
                if not self._serial or not self._serial.is_open:
                    self._auto_connect()
                    time.sleep(2)
                    continue

                # 发送寻卡/读卡命令
                self._send_query()

                # 等待响应
                time.sleep(0.5)
                data = b""
                deadline = time.time() + 2.0
                while time.time() < deadline:
                    n = self._serial.in_waiting
                    if n:
                        chunk = self._serial.read(n)
                        data += chunk
                        deadline = time.time() + 0.5  # 有新数据则延长等待
                    else:
                        time.sleep(0.1)

                if data:
                    self._log(f"收到 {len(data)} bytes")
                    result = self._decode(data)
                    if result and self.on_signin:
                        self._log(f"解析: {result['name']} {result['id_number']}")
                        try:
                            self.on_signin(result["name"], result["id_number"], "", result)
                        except Exception as e:
                            logger.error(f"签到回调: {e}")
                    elif result is None:
                        self._log(f"未识别: {data[:80].hex()}")
                else:
                    time.sleep(1)
            except (OSError, serial.SerialException) as e:
                self._log(f"串口断开: {e}")
                self._close()
                time.sleep(3)
            except Exception as e:
                self._log(f"异常: {e}")
                time.sleep(1)

    _query_cache = None

    def _send_query(self):
        """发送寻卡/读卡命令，自动尝试多种协议"""
        if not self._serial or not self._serial.is_open:
            return

        # 缓存：一次连接只测一次协议
        if self._query_cache is None:
            self._query_cache = self._detect_protocol()

        cmd = self._query_cache
        if cmd:
            try:
                self._serial.reset_input_buffer()
                self._serial.write(cmd)
            except Exception:
                pass

    def _detect_protocol(self):
        """自动检测读卡器协议，发送测试命令看是否有响应"""
        import serial

        # 常用寻卡命令
        candidates = {
            "cmd_A": b'\xAA\xAA\xAA\x96\x69\x00\x03\x20\x01\x22',   # 通用寻卡
            "cmd_B": b'\xAA\xAA\xAA\x96\x69\x00\x03\x22\x01\x24',   # 通用读卡
            "cmd_C": b'\x7E\x01\x00\x00\x00\x00\x7E',               # 简单协议
            "cmd_D": b'\x02\x00\x00\x00\x00\x03',                   # STX/ETX
            "cmd_E": b'\xAB\xCD\x00\x01\x00\x00\x00\x00\xEF\x01',   # 华大系列
        }

        for name, cmd in candidates.items():
            try:
                self._serial.reset_input_buffer()
                self._serial.write(cmd)
                time.sleep(0.3)
                n = self._serial.in_waiting
                if n > 0:
                    resp = self._serial.read(min(n, 200))
                    self._log(f"协议 {name} 有响应: {len(resp)} bytes {resp[:40].hex()}")
                    return cmd
            except Exception:
                continue
            time.sleep(0.1)

        self._log("自动探测完成，使用被动监听模式")
        return b""  # 被动模式：不发送命令，只监听

    def _auto_connect(self):
        import serial
        ports = self._list_ports()
        if not ports:
            return  # 没串口，等下次循环

        for dev, desc in ports:
            self._log(f"尝试 {dev} ({desc})")
            for baud in [115200, 9600, 57600, 19200]:
                try:
                    s = serial.Serial(dev, baud, timeout=0.3)
                    time.sleep(0.2)

                    # 试发命令看是否有响应
                    test_cmds = [
                        b'\xAA\xAA\xAA\x96\x69\x00\x03\x20\x01\x22',
                        b'\x7E\x01\x00\x00\x00\x00\x7E',
                    ]
                    found = False
                    for cmd in test_cmds:
                        try:
                            s.reset_input_buffer()
                            s.write(cmd)
                            time.sleep(0.15)
                            if s.in_waiting:
                                resp = s.read(min(s.in_waiting, 100))
                                self._log(f"  {dev}@{baud} 响应: {len(resp)} bytes")
                                found = True
                                break
                        except Exception:
                            continue

                    if found or any(kw in desc.lower() for kw in ["usb", "serial", "ch340", "cp210", "com", "uart", "id", "card", "reader", "身份证", "读卡"]):
                        self._serial = s
                        self.port = dev
                        self._query_cache = None
                        self._log(f"已连接 {dev} @ {baud}")
                        return

                    s.close()
                except Exception:
                    continue

    def _close(self):
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None
        self._query_cache = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()
        print("[COM读卡器] 全自动模式启动 — 扫描端口 + 探测协议 + 定时查询")

    def stop(self):
        self._running = False
        self._close()
        print("[COM读卡器] 已停止")
