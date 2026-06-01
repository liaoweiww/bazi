"""
读卡器 — 回到能扫到的版本 + 剪贴板辅助
"""
import re, time, threading, os

if os.name != "nt":
    class WindowCardReader:
        def __init__(self, *a, **kw): pass; def start(self): pass; def stop(self): pass
else:
    import ctypes; from ctypes import wintypes
    u32 = ctypes.windll.user32
    ID_RE = re.compile(r'(\d{17}[\dXx])')
    NAME_RE = re.compile(r'[一-鿿]{2,4}')
    BAD = {"姓名","性别","民族","出生","住址","签发","有效期","号码","机关","读卡","离线","在线","检测","请插入","Microsoft","Windows","Program","Default","确定","取消","关闭","设置","测试","帮助","MSCTF","GDI","IME","开始","任务栏","----","-->"}

    class WindowCardReader:
        def __init__(self, config=None, on_signin=None):
            self.debug = True
            self.on_signin = on_signin
            self._seen = set()
            self._running = False

        def _log(self, msg):
            if self.debug: print(f"[窗口读卡] {msg}")

        def _snap(self):
            texts = set()
            KW = ["读卡","身份证","Card","reader","鱼住","sam","离线","ReadCard","TForm","fmIDInfo","fmID"]

            def e(h, _):
                if not u32.IsWindowVisible(h): return True
                c = ctypes.create_unicode_buffer(256); u32.GetClassNameW(h, c, 256)
                t = ctypes.create_unicode_buffer(256); u32.GetWindowTextW(h, t, 256)
                check = f"{t.value} {c.value}"
                if any(k in check for k in KW):
                    # 读主窗口
                    for sz in [256,1024]:
                        cb = ctypes.create_unicode_buffer(sz)
                        u32.GetWindowTextW(h, cb, sz)
                        if cb.value: texts.add(cb.value.strip())
                        r = u32.SendMessageW(h, 0x000D, sz, ctypes.cast(cb, ctypes.c_void_p))
                        if r > 0 and cb.value: texts.add(cb.value.strip())
                    # 读子窗口
                    def ce(ch, _2):
                        for sz in [256,1024]:
                            cb2 = ctypes.create_unicode_buffer(sz)
                            u32.GetWindowTextW(ch, cb2, sz)
                            if cb2.value: texts.add(cb2.value.strip())
                            r2 = u32.SendMessageW(ch, 0x000D, sz, ctypes.cast(cb2, ctypes.c_void_p))
                            if r2 > 0 and cb2.value: texts.add(cb2.value.strip())
                        return True
                    CC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
                    try: u32.EnumChildWindows(h, CC(ce), 0)
                    except: pass
                return True
            WC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
            u32.EnumWindows(WC(e), 0)
            return texts

        def _loop(self):
            self._log("已启动")
            last = ""
            while self._running:
                try:
                    all_t = sorted(self._snap())
                    text = " ".join(all_t)
                    if text != last and text:
                        last = text
                        # 始终输出扫描结果（方便诊断）
                        if text.strip():
                            self._log(f"扫描: {text[:250]}")
                        ids = set(ID_RE.findall(text))
                        new = ids - self._seen
                        if new:
                            self._seen |= ids
                            r = self._parse(text)
                            if r:
                                self._log(f">>> 抓到: {r['name']} {r['id_number']}")
                                if self.on_signin:
                                    self.on_signin(r["name"], r["id_number"], text, r)
                except Exception as e:
                    self._log(f"异常: {e}")
                time.sleep(2)

        def _parse(self, text):
            m = ID_RE.search(text)
            if not m: return None
            idn = m.group(1).upper()
            w = [7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2]; cc = "10X98765432"
            try:
                if len(idn)==18 and idn[17].upper() != cc[sum(w[i]*int(idn[i]) for i in range(17))%11]:
                    return None
            except: pass
            name = ""
            for mx in NAME_RE.finditer(text):
                n = mx.group()
                if n not in BAD and len(n) >= 2:
                    name = n; break
            return {"name": name or "未知", "id_number": idn}

        def start(self):
            self._running = True
            threading.Thread(target=self._loop, daemon=True).start()
            import datetime as _dt
            self._log(f"已启动(代码 {_dt.datetime.fromtimestamp(os.path.getmtime(__file__)).strftime('%H:%M:%S')}) - 请打开读卡测试程序并放上身份证")

        def stop(self):
            self._running = False
