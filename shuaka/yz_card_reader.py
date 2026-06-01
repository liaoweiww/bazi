"""
鱼住 YNR201 身份证读卡器 — WebSocket 服务模式
通过 yzwlReadCardServer Windows 服务（ws://127.0.0.1:30004/ws）获取刷卡数据
支持多个客户端同时连接，不会独占硬件
纯标准库实现，无需额外 pip 依赖
"""
import json
import base64
import struct
import socket
import threading
import time
import os
import re


class YzCardReader:
    """鱼住 YNR201 身份证读卡器（通过 yzwlReadCardServer WebSocket）"""

    def __init__(self, config=None, on_signin=None):
        self.on_signin = on_signin
        self.config = config or {}
        self.debug = self.config.get("debug", True)
        self._running = False
        self._sock = None
        self._last_id = ""

    def _log(self, msg):
        if self.debug:
            print(f"[鱼住读卡] {msg}")

    # ========== 极简 WebSocket 客户端（纯 socket，零依赖） ==========

    @staticmethod
    def _ws_connect(host, port, path="/ws", timeout=5):
        """WebSocket 握手连接，返回 socket 对象"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))

        # 生成随机 key
        import random as _r
        key_bytes = bytes(_r.randint(0, 255) for _ in range(16))
        key = base64.b64encode(key_bytes).decode()

        # HTTP Upgrade 请求
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        )
        sock.sendall(request.encode())

        # 读取响应
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = sock.recv(4096)
            if not chunk:
                raise ConnectionError("WebSocket 握手失败：服务器关闭连接")
            response += chunk

        response_str = response.decode('utf-8', errors='replace')
        if "101" not in response_str.split("\r\n")[0]:
            raise ConnectionError(f"WebSocket 握手失败: {response_str.split(chr(13)+chr(10))[0]}")

        sock.settimeout(None)  # 后续用阻塞模式接收
        return sock

    @staticmethod
    def _ws_recv(sock):
        """接收一个 WebSocket 文本帧，返回字符串；连接关闭返回 None"""
        while True:
            header = b""
            while len(header) < 2:
                b = sock.recv(1)
                if not b:
                    return None
                header += b

            opcode = header[0] & 0x0F
            masked = (header[1] & 0x80) != 0
            length = header[1] & 0x7F

            if length == 126:
                length = struct.unpack(">H", sock.recv(2))[0]
            elif length == 127:
                length = struct.unpack(">Q", sock.recv(8))[0]

            if masked:
                mask_key = sock.recv(4)

            payload = b""
            while len(payload) < length:
                remaining = length - len(payload)
                chunk = sock.recv(min(remaining, 4096))
                if not chunk:
                    return None
                payload += chunk

            if masked:
                payload = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))

            if opcode == 0x8:  # Close
                return None
            elif opcode == 0x9:  # Ping
                pong = bytes([0x8A, 0x00])
                sock.sendall(pong)
                continue
            elif opcode == 0x1:  # Text
                return payload.decode('utf-8', errors='replace')
            # 忽略其他帧类型

    @staticmethod
    def _ws_send(sock, text):
        """发送一个 WebSocket 文本帧"""
        payload = text.encode('utf-8')
        length = len(payload)
        frame = bytearray()
        frame.append(0x81)  # FIN + Text opcode
        if length < 126:
            frame.append(length)
        elif length < 65536:
            frame.append(126)
            frame.extend(struct.pack(">H", length))
        else:
            frame.append(127)
            frame.extend(struct.pack(">Q", length))
        frame.extend(payload)
        sock.sendall(bytes(frame))

    # ========== 数据解析 ==========

    @staticmethod
    def _decode_field(b64_val):
        """解码 CardInfo 字段：base64 → UTF-16LE 字节 → 字符串"""
        if not b64_val:
            return ""
        try:
            raw = base64.b64decode(b64_val)
            return raw.decode('utf-16-le', errors='replace').rstrip('\x00').strip()
        except Exception:
            return ""

    @staticmethod
    def _parse_card_message(user_param_b64):
        """解析服务推送的刷卡数据（UserParam 是 base64 编码的 JSON）"""
        try:
            user_param = json.loads(base64.b64decode(user_param_b64).decode('utf-8'))
        except Exception:
            return None

        card_info = user_param.get('CardInfo', {})
        if not card_info:
            return None

        name = YzCardReader._decode_field(card_info.get('Name', ''))
        id_number = YzCardReader._decode_field(card_info.get('No', ''))
        if not name or not id_number:
            return None

        return {
            'name': name,
            'id_number': id_number,
            'sex': YzCardReader._decode_field(card_info.get('Sex', '')),
            'nation': YzCardReader._decode_field(card_info.get('Nation', '')),
            'birth': YzCardReader._decode_field(card_info.get('Birthday', '')),
            'address': YzCardReader._decode_field(card_info.get('Address', '')),
        }

    # ========== 消息循环 ==========

    def _ws_loop(self):
        """WebSocket 消息循环（带自动重连）"""
        print("[鱼住读卡] 读卡线程已启动（WebSocket 服务模式）")

        ws_url = self.config.get('ws_url', 'ws://127.0.0.1:30004/ws')
        m = re.match(r'ws://([^:/]+):?(\d+)?(/.*)?', ws_url)
        host = m.group(1) if m else '127.0.0.1'
        port = int(m.group(2)) if m and m.group(2) else 30004
        path = m.group(3) if m and m.group(3) else '/ws'

        while self._running:
            try:
                self._log(f"连接 {host}:{port}{path} ...")
                sock = self._ws_connect(host, port, path, timeout=5)
                self._sock = sock
                print(f"[鱼住读卡] 已连接到读卡服务 ws://{host}:{port}{path}，等待刷卡...")

                # 通知管理面板
                try:
                    from web_server import set_monitor_card_online
                    set_monitor_card_online(True)
                except ImportError:
                    pass

                while self._running:
                    msg = self._ws_recv(sock)
                    if msg is None:
                        break  # 连接关闭

                    try:
                        data = json.loads(msg)
                    except json.JSONDecodeError:
                        continue

                    if data.get('Ret') != 0:
                        self._log(f"服务错误: {data.get('ErrInfo', '')}")
                        continue

                    if data.get('Cmd') == 10001:
                        result = self._parse_card_message(data.get('UserParam', ''))
                        if result:
                            idn = result['id_number']
                            if idn != self._last_id:
                                self._last_id = idn
                                self._log(f">>> 签到: {result['name']} {idn}")
                                if self.on_signin:
                                    self.on_signin(result['name'], idn, '', result)

            except Exception as e:
                if self._running:
                    self._log(f"连接异常: {e}")

            finally:
                try:
                    from web_server import set_monitor_card_online
                    set_monitor_card_online(False)
                except ImportError:
                    pass
                if self._sock:
                    try:
                        self._sock.close()
                    except Exception:
                        pass
                    self._sock = None

            if self._running:
                print("[鱼住读卡] 连接断开，3秒后重连...")
                time.sleep(3)

        print("[鱼住读卡] 读卡线程已退出")

    # ========== 公共接口 ==========

    def start(self):
        print("[鱼住读卡] start() 被调用")
        if os.name != "nt":
            print("[鱼住读卡] 当前仅支持 Windows（需要 yzwlReadCard 服务）")
            return
        self._running = True
        threading.Thread(target=self._ws_loop, daemon=True).start()
        print("[鱼住读卡] 已启动（WebSocket 服务模式）")

    def stop(self):
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
        self._log("正在停止...")
