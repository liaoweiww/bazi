"""签到系统 — 桌面控制面板 · 优雅版"""
import sys, os, time, json, threading, shutil, urllib.request

if sys.platform == 'win32':
    LOCAL_DIR = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'shuaka')
    SMB_SRC = r'\\192.168.50.226\shuaka'
else:
    LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
    SMB_SRC = LOCAL_DIR

def sync_code():
    if SMB_SRC == LOCAL_DIR: return True, "本地运行，无需同步"
    if not os.path.exists(os.path.join(SMB_SRC, 'main.py')): return False, "无法访问 SMB 共享"
    try:
        count = 0; errs = []; os.makedirs(LOCAL_DIR, exist_ok=True)
        SYNC_EXT = ('.py','.dll','.ini','.bat','.yaml','.txt','.md','.ico','.png')
        SYNC_FILES = ('config.yaml','VERSION')
        for fn in os.listdir(SMB_SRC):
            if os.path.splitext(fn)[1].lower() in SYNC_EXT or fn in SYNC_FILES:
                sp, dp = os.path.join(SMB_SRC, fn), os.path.join(LOCAL_DIR, fn)
                if os.path.isfile(sp):
                    try: shutil.copy2(sp, dp); count += 1
                    except: errs.append(fn)
        ts, td = os.path.join(SMB_SRC, 'tablet'), os.path.join(LOCAL_DIR, 'tablet')
        if os.path.isdir(ts):
            os.makedirs(td, exist_ok=True)
            for fn in os.listdir(ts):
                sf, df = os.path.join(ts, fn), os.path.join(td, fn)
                if os.path.isfile(sf):
                    try: shutil.copy2(sf, df); count += 1
                    except: errs.append(f"tablet/{fn}")
        total = count + len(errs)
        for cd in __import__('glob').glob(os.path.join(LOCAL_DIR, '__pycache__')):
            try: shutil.rmtree(cd)
            except: pass
        return True, f"同步完成 {count}/{total} ✓" if not errs else f"同步 {count}/{total}，{len(errs)} 失败"
    except Exception as e: return False, str(e)

def start_server():
    if getattr(sys, 'frozen', False):
        bd = sys._MEIPASS
        for d in ['tablet']:
            s, t = os.path.join(bd, d), os.path.join(LOCAL_DIR, d)
            if os.path.exists(s) and not os.path.exists(t): shutil.copytree(s, t)
        for f in ['config.yaml']:
            s, t = os.path.join(bd, f), os.path.join(LOCAL_DIR, f)
            if os.path.exists(s) and not os.path.exists(t): shutil.copy2(s, t)
    os.chdir(LOCAL_DIR)
    if LOCAL_DIR not in sys.path: sys.path.insert(0, LOCAL_DIR)
    import main; main.main()

def build_gui():
    import customtkinter as ctk
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("身份证签到系统 · 控制面板")
    w, h = 560, 640
    app.geometry(f"{w}x{h}")
    app.update_idletasks()
    sw, sh = app.winfo_screenwidth(), app.winfo_screenheight()
    app.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
    app.resizable(False, False)

    app.configure(fg_color="#0a0e14")

    app.grid_rowconfigure(5, weight=1)
    app.grid_columnconfigure(0, weight=1)

    # ====== 头部（渐变文字效果） ======
    hdr = ctk.CTkFrame(app, fg_color="transparent")
    hdr.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 6))
    ctk.CTkLabel(hdr, text="身份证签到系统",
                 font=ctk.CTkFont(size=22, weight="bold"), text_color="#e6edf3").pack()
    ver_label = ctk.CTkLabel(hdr, text="", font=ctk.CTkFont(size=10), text_color="#5a6a80")
    ver_label.pack()

    # ====== 提示条 ======
    alert = ctk.CTkFrame(app, fg_color="#151d2b", corner_radius=8, height=30)
    alert.grid(row=1, column=0, sticky="ew", padx=20, pady=(4, 0))
    alert_label = ctk.CTkLabel(alert, text="", font=ctk.CTkFont(size=12, weight="bold"))
    alert_label.pack(expand=True)
    _alert_job = [None]

    def show_alert(text, color="#8b9bb4", duration=2500):
        alert_label.configure(text=text, text_color=color)
        alert.grid()
        if _alert_job[0]: app.after_cancel(_alert_job[0])
        _alert_job[0] = app.after(duration, lambda: alert.grid_remove())

    # ====== 进度条 ======
    pbar = ctk.CTkProgressBar(app, height=5, corner_radius=3, progress_color="#58a6ff",
                               fg_color="#121a24", mode="determinate")
    pbar.set(0)
    pbar.grid(row=3, column=0, sticky="ew", padx=20, pady=(2, 4))
    pbar.grid_remove()

    def show_progress():
        pbar.set(0); pbar.grid()
        def _step(v=0):
            if v <= 0.9:
                pbar.set(v)
                r, g, b = int(0x58+v*(0x3f-0x58)), int(0xa6+v*(0xb9-0xa6)), int(0xff+v*(0x50-0xff))
                pbar.configure(progress_color=f"#{r:02x}{g:02x}{b:02x}")
                app.after(60, lambda: _step(v+0.03))
        _step()

    def finish_progress(ok=True):
        pbar.set(1)
        pbar.configure(progress_color="#3fb950" if ok else "#f85149")
        app.after(600, lambda: (pbar.grid_remove(), pbar.set(0)))

    # ====== 状态卡片（精致阴影 + 轻盈动画） ======
    stats = ctk.CTkFrame(app, fg_color="transparent")
    stats.grid(row=2, column=0, sticky="ew", padx=14, pady=6)
    for i in range(4): stats.grid_columnconfigure(i, weight=1)

    cards = {}
    CARD_COLORS = {
        "svc": ("#1a3a2a", "#1a2f1a"), "reader": ("#1a2a3a", "#1a2535"),
        "today": ("#1a2a3a", "#1a2535"), "total": ("#2a1a3a", "#251a35"),
        "sync": ("#1a3a3a", "#1a2f2f"), "last": ("#1a2a3a", "#1a2535"),
        "voice": ("#2a2a1a", "#252a1a"), "uptime": ("#1a2a3a", "#1a2535"),
    }
    items = [
        ("svc",0,0,"服务状态","●"),("reader",0,1,"读卡器","●"),
        ("today",0,2,"今日签到",""),("total",0,3,"累计刷卡",""),
        ("sync",1,0,"数据同步","●"),("last",1,1,"最近签到",""),
        ("voice",1,2,"语音播报","●"),("uptime",1,3,"运行时长",""),
    ]
    for key, r, c, title, icon in items:
        g1, g2 = CARD_COLORS.get(key, ("#1a2530", "#1a2030"))
        card = ctk.CTkFrame(stats, fg_color=g1, corner_radius=10,
                            border_color="#1e3040", border_width=1)
        card.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(8, 0))
        ctk.CTkLabel(top, text=title, font=ctk.CTkFont(size=9),
                     text_color="#7a8ea0").pack(side="left")
        dot = ctk.CTkLabel(top, text=icon, font=ctk.CTkFont(size=10), text_color="#3a5060")
        dot.pack(side="right")
        val = ctk.CTkLabel(card, text="--", font=ctk.CTkFont(size=15, weight="bold"),
                            text_color="#c8d6e5")
        val.pack(anchor="w", padx=10, pady=(2, 10))
        cards[key] = (dot, val, card)

    def flash_card(key, c="#3fb950"):
        _, _, card = cards[key]; orig = card.cget("fg_color")
        card.configure(fg_color=c)
        app.after(300, lambda: card.configure(fg_color=orig))

    # ====== API ======
    def api(path, method="GET", data=None):
        try:
            req = urllib.request.Request(f"http://127.0.0.1:5002{path}", method=method)
            req.add_header("Content-Type", "application/json")
            if not path.endswith("/login") and _token[0]:
                req.add_header("X-Auth-Token", _token[0])
            if data: req.data = json.dumps(data).encode()
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode())
        except Exception as e: return {"ok": False, "error": str(e)}

    _token = [""]
    def auto_login():
        r = api("/api/login", "POST", {"username": "admin", "password": "admin123"})
        if r.get("ok"): _token[0] = r.get("token", "")
        return r.get("ok", False)

    # ====== 按钮 ======
    btns = ctk.CTkFrame(app, fg_color="transparent")
    btns.grid(row=4, column=0, sticky="ew", padx=16, pady=4)

    def make_btn(parent, text, fg, hover, cmd, h=38, border=False):
        orig_text = text
        def _click():
            btn.configure(text="✓ " + orig_text[2:], fg_color="#1a7f37", state="disabled")
            app.update_idletasks()
            app.after(600, lambda: btn.configure(text=orig_text, fg_color=fg, state="normal"))
            if cmd: threading.Thread(target=cmd, daemon=True).start()
        btn = ctk.CTkButton(parent, text=orig_text, command=_click,
                            fg_color=fg, hover_color=hover, cursor="hand2",
                            font=ctk.CTkFont(size=13, weight="bold"), height=h, corner_radius=10)
        if border: btn.configure(border_width=1, border_color="#2a3a4a")
        return btn

    def do_sync_lan():
        log_add("🏠", "局域网同步中...", "#58a6ff")
        show_alert("同步中...", "#58a6ff", 4000); show_progress()
        def _run():
            r = api("/api/sync_lan", "POST")
            ok = r.get("ok", False); msg = r.get("message") or r.get("error", "")
            log_add("✅" if ok else "❌", msg, "#3fb950" if ok else "#f85149")
            show_alert(msg, "#3fb950" if ok else "#f85149")
            app.after(0, lambda: finish_progress(ok))
        threading.Thread(target=_run, daemon=True).start()

    def do_sync_remote():
        log_add("🌍", "远程升级中...", "#58a6ff")
        show_alert("远程升级中...", "#58a6ff", 4000); show_progress()
        def _run():
            r = api("/api/sync_remote", "POST")
            ok = r.get("ok", False); msg = r.get("message") or r.get("error", "")
            log_add("✅" if ok else "❌", msg, "#3fb950" if ok else "#f85149")
            show_alert(msg, "#3fb950" if ok else "#f85149")
            app.after(0, lambda: finish_progress(ok))
        threading.Thread(target=_run, daemon=True).start()

    def do_restart():
        show_alert("重启中...", "#d29922", 4000); api("/api/restart", "POST")

    def do_open(path, label):
        import webbrowser
        webbrowser.open(f"http://127.0.0.1:5002{path}?_t={int(time.time())}")
        show_alert(f"已打开 {label}", "#8b9bb4")

    def do_rebuild():
        log_add("🔧", "Rebuilding EXE...", "#d29922")
        show_alert("Building EXE...", "#d29922", 120000); show_progress()
        def _run():
            import subprocess as _sp
            _dd = os.path.join(LOCAL_DIR, 'dist')
            _old = os.path.join(_dd, 'qiandao.exe')
            if os.path.exists(_old):
                try: os.remove(_old)
                except: pass
            _icon = os.path.join(LOCAL_DIR, 'icon.ico')
            _cmd = ['python', '-m', 'PyInstaller', '--onefile', '--windowed',
                    '--name', 'qiandao', '--add-data', 'tablet;tablet',
                    '--add-data', 'config.yaml;.', '--hidden-import', 'customtkinter',
                    '--hidden-import', '_socket', '--hidden-import', 'socket',
                    '--collect-all', 'tkinter',
                    '--clean', 'desktop_app.py']
            if os.path.exists(_icon): _cmd.insert(3, '--icon=icon.ico')
            _ok = False
            try:
                _r = _sp.run(_cmd, cwd=LOCAL_DIR, capture_output=True, text=True, timeout=300)
                if _r.returncode == 0 and os.path.exists(_old):
                    _desk = os.path.join(os.environ.get('USERPROFILE', os.path.expanduser('~')), 'Desktop')
                    _dst = os.path.join(_desk, 'qiandao_new.exe')
                    if os.path.exists(_dst):
                        try: os.remove(_dst)
                        except: pass
                    shutil.copy2(_old, _dst)
                    _ok = True
                    log_add("✅", "qiandao_new.exe ready", "#3fb950")
                    show_alert("Done! Restart qiandao.exe", "#3fb950", 8000)
                else:
                    log_add("❌", f"Failed: {_r.stderr[:100]}", "#f85149")
                    show_alert("Build failed", "#f85149")
            except Exception as e:
                log_add("❌", f"Error: {e}", "#f85149")
            app.after(0, lambda ok=_ok: finish_progress(ok))
        threading.Thread(target=_run, daemon=True).start()

    def do_exit():
        api("/api/shutdown", "POST"); app.destroy()

    # 按钮行1
    r1 = ctk.CTkFrame(btns, fg_color="transparent"); r1.pack(fill="x", pady=3)
    r1.grid_columnconfigure((0, 1), weight=1)
    make_btn(r1, "🏠 局域网同步", "#1a5c2a", "#1f7033", do_sync_lan).grid(row=0, column=0, padx=4, sticky="ew")
    make_btn(r1, "🌍 远程升级", "#1a3d5c", "#1f4d70", do_sync_remote).grid(row=0, column=1, padx=4, sticky="ew")

    # 按钮行2
    r2 = ctk.CTkFrame(btns, fg_color="transparent"); r2.pack(fill="x", pady=5)
    r2.grid_columnconfigure((0, 1, 2), weight=1)
    make_btn(r2, "🔌 重启服务", "#151d28", "#1e2938", do_restart, border=True).grid(row=0, column=0, padx=4, sticky="ew")
    make_btn(r2, "⚙ 管理后台", "#151d28", "#1e2938", lambda: do_open("/admin", "管理后台"), border=True).grid(row=0, column=1, padx=4, sticky="ew")
    make_btn(r2, "📺 大屏展示", "#151d28", "#1e2938", lambda: do_open("/", "大屏展示"), border=True).grid(row=0, column=2, padx=4, sticky="ew")

    # ====== 日志 ======
    log_frame = ctk.CTkFrame(app, fg_color="#0f1820", corner_radius=10,
                              border_color="#1a2a38", border_width=1)
    log_frame.grid(row=5, column=0, sticky="nsew", padx=16, pady=6)
    log_frame.grid_rowconfigure(1, weight=1); log_frame.grid_columnconfigure(0, weight=1)

    lh = ctk.CTkFrame(log_frame, fg_color="transparent")
    lh.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
    ctk.CTkLabel(lh, text="📋 实时日志", font=ctk.CTkFont(size=12, weight="bold"),
                 text_color="#7a8ea0").pack(side="left")
    log_count = ctk.CTkLabel(lh, text="", font=ctk.CTkFont(size=10), text_color="#4a5a6a")
    log_count.pack(side="right")

    log_box = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(size=10, family="Consolas,monospace"),
                              fg_color="#0a1018", text_color="#7a8ea0", wrap="word",
                              corner_radius=0, border_width=0)
    log_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=(4, 10))
    log_box.configure(state="disabled"); _ll = [0]

    def log_add(icon, msg, color="#7a8ea0"):
        log_box.configure(state="normal")
        t = time.strftime("%H:%M:%S")
        log_box.insert("end", f"{icon} [{t}] {msg}\n")
        ln = int(log_box.index("end-1c").split(".")[0]) - 1
        log_box.tag_add(f"c{ln}", f"{ln}.0", f"{ln}.end")
        log_box.tag_config(f"c{ln}", foreground=color)
        log_box.see("end"); log_box.configure(state="disabled")
        _ll[0] += 1; log_count.configure(text=f"{_ll[0]} lines")
        if _ll[0] > 300:
            log_box.configure(state="normal"); log_box.delete("1.0", "3.0"); log_box.configure(state="disabled")

    # ====== 退出 ======
    exit_frame = ctk.CTkFrame(app, fg_color="transparent")
    exit_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 10))
    ctk.CTkButton(exit_frame, text="⏻ 退出系统", command=do_exit,
                  fg_color="transparent", border_color="#4a2030", border_width=1,
                  text_color="#e05570", hover_color="#2d1216", cursor="hand2",
                  font=ctk.CTkFont(size=11), height=28, width=110).pack()

    # ====== 状态轮询 ======
    last_name = ""; total_signs = [0]; start_time = time.time()
    was_offline = [False]; reader_was_on = [False]; prev_vals = {}
    warmup = [True]
    # 每个卡片的独立动画相位
    anim_phase = {k: i*7 for i, k in enumerate(cards.keys())}

    def poll():
        app.after(1500, poll)
        def _fetch_update():
            try:
                req = urllib.request.Request("http://127.0.0.1:5002/api/monitor")
                with urllib.request.urlopen(req, timeout=3) as r: d = json.loads(r.read().decode())
            except Exception:
                app.after(0, lambda: (
                    log_add("❌", "服务连接失败", "#f85149") if not was_offline[0] and not warmup[0] else None,
                    was_offline.__setitem__(0, True)
                )); return

            def _ui():
                nonlocal last_name
                if was_offline[0]: was_offline[0] = False; log_add("✅", "服务已恢复", "#3fb950")
                cr = d.get("card_reader", {}); sy = d.get("sync", {}); ed = d.get("excel_dir", {})
                svc_up = bool(d.get("started_at")); ver_label.configure(text=d.get("version", ""))

                # 全局动画tick
                t = anim_phase["svc"] = (anim_phase.get("svc", 0) + 1) % 60
                
                # 动画辅助函数：呼吸效果
                def _breathe(key, active, color_on="#3fb950", color_off="#484f58"):
                    ph = (t + anim_phase.get(key, 0)) % 60 / 30.0
                    sz = int(10 + 5 * (1 - abs(ph - 1))) if active else 10
                    bright = 0.4 + 0.6 * (1 - abs(ph - 1)) if active else 1.0
                    cr = int(int(color_on[1:3], 16) * bright)
                    cg = int(int(color_on[3:5], 16) * bright)
                    cb = int(int(color_on[5:7], 16) * bright)
                    col = f"#{cr:02x}{cg:02x}{cb:02x}" if active else color_off
                    cards[key][0].configure(text_color=col, font=ctk.CTkFont(size=sz))
                
                g = "#3fb950" if svc_up else "#f85149"
                _breathe("svc", svc_up, "#3fb950", g if not svc_up else "#484f58")
                cards["svc"][1].configure(text="运行中" if svc_up else "未启动", text_color=g)

                tr = cr.get("total_reads", 0)
                if cr.get("online"):
                    _breathe("reader", True, "#3fb950")
                    cards["reader"][0].configure(text_color="#3fb950")
                    cards["reader"][1].configure(text=f"在线 · {tr}张", text_color="#3fb950")
                    if not reader_was_on[0]: reader_was_on[0] = True; log_add("💳", "读卡器已连接", "#3fb950"); flash_card("reader")
                elif cr.get("enabled"):
                    cards["reader"][0].configure(text_color="#d29922"); cards["reader"][1].configure(text="扫描中...", text_color="#d29922"); reader_was_on[0] = False
                else:
                    cards["reader"][0].configure(text_color="#484f58"); cards["reader"][1].configure(text="已禁用", text_color="#484f58"); reader_was_on[0] = False

                nf = len(ed.get("files", []))
                if nf != prev_vals.get("today"): prev_vals["today"] = nf; flash_card("today", "#1a3a5c")
                _breathe("today", nf > 0, "#58a6ff")
                cards["today"][1].configure(text=f"{nf}", text_color="#58a6ff")

                if tr != prev_vals.get("total"): prev_vals["total"] = tr; flash_card("total", "#2d1a4a")
                total_signs[0] = max(total_signs[0], tr)
                _breathe("total", total_signs[0] > 0, "#a371f7")
                cards["total"][1].configure(text=f"{total_signs[0]}", text_color="#a371f7")

                sl = sy.get("last_sync", "")
                synced = bool(sl) or sy.get("enabled")
                _breathe("sync", synced, "#3fb950")
                cards["sync"][0].configure(text_color="#3fb950" if synced else "#484f58")
                cards["sync"][1].configure(text=f"✓ {sl[-8:]}" if sl else ("坚果云同步" if sy.get("enabled") else "未启用"),
                                           text_color="#3fb950" if synced else "#484f58")

                last = cr.get("last_name", ""); lid = cr.get("last_id", "")
                if last:
                    _breathe("last", True, "#c8d6e5")
                    cards["last"][1].configure(text=last, text_color="#c8d6e5")
                    if last != last_name:
                        last_name = last; total_signs[0] += 1 if tr == 0 else 0
                        log_add("✅", f"签到: {last} {lid}", "#3fb950")
                        flash_card("last", "#1a3a2a"); show_alert(f"🎉 {last} 签到成功！", "#3fb950")
                else:
                    cards["last"][1].configure(text="等待刷卡...", text_color="#484f58")

                _breathe("voice", True, "#e8b830")
                cards["voice"][0].configure(text_color="#3fb950"); cards["voice"][1].configure(text="就绪", text_color="#3fb950")
                up = int(time.time() - start_time); h, m, s = up // 3600, (up % 3600) // 60, up % 60
                cards["uptime"][1].configure(text=f"{h}:{m:02d}:{s:02d}", text_color="#7a8ea0")

            app.after(0, _ui)
        threading.Thread(target=_fetch_update, daemon=True).start()

    # ====== 初始化 ======
    def try_login():
        for i in range(10):
            if auto_login(): log_add("🔑", "已登录", "#3fb950"); return
            time.sleep(2)
        log_add("⚠️", "登录失败", "#d29922")
    threading.Thread(target=try_login, daemon=True).start()

    log_add("🚀", "签到系统 v2.0", "#58a6ff")
    log_add("📡", "Flask: http://127.0.0.1:5002", "#7a8ea0")
    log_add("💳", "读卡器: WebSocket 模式", "#7a8ea0")
    log_add("🔊", "语音播报: 就绪", "#7a8ea0")
    if SMB_SRC != LOCAL_DIR: log_add("🏠", f"局域网同步: {SMB_SRC}", "#7a8ea0")

    app.after(10000, lambda: warmup.__setitem__(0, False))
    app.after(2000, poll)
    return app

if __name__ == '__main__':
    # 自动应用更新
    _desktop = os.path.join(os.environ.get('USERPROFILE', os.path.expanduser('~')), 'Desktop')
    _new_exe = os.path.join(_desktop, 'qiandao_new.exe')
    _cur_exe = os.path.join(_desktop, 'qiandao.exe')
    if os.path.exists(_new_exe):
        import tempfile, subprocess as _sp2
        _script = os.path.join(tempfile.gettempdir(), '_upgrade_qiandao.py')
        with open(_script, 'w') as f:
            f.write(f'''import time, os, shutil
time.sleep(2)
desktop = r"{_desktop}"
new_exe = r"{_new_exe}"
cur_exe = r"{_cur_exe}"
try: os.remove(cur_exe)
except: pass
try: shutil.move(new_exe, cur_exe)
except: pass
try: os.startfile(cur_exe)
except: pass
''')
        _sp2.Popen([sys.executable, _script], creationflags=0x00000008 if sys.platform == 'win32' else 0)
        sys.exit(0)

    os.chdir(LOCAL_DIR)
    if LOCAL_DIR not in sys.path: sys.path.insert(0, LOCAL_DIR)

    # 轻量升级提醒（超过7天未更新才提示，不自动构建）
    if getattr(sys, 'frozen', False):
        _disk_py = os.path.join(LOCAL_DIR, 'desktop_app.py')
        if os.path.exists(_disk_py) and os.path.exists(_cur_exe):
            if os.path.getmtime(_disk_py) > os.path.getmtime(_cur_exe) + 604800:
                import tkinter.messagebox as _mb
                _r = __import__('tkinter').Tk(); _r.withdraw()
                _mb.showinfo('Update', 'New version available.\nRun build_exe.bat to update.')
                _r.destroy()

    # 直接渲染 GUI（EXE 内嵌最新代码）
    app = build_gui()

    def _bg_init():
        _icon_src = os.path.join(SMB_SRC, 'icon.ico')
        _icon_dst = os.path.join(LOCAL_DIR, 'icon.ico')
        if os.path.exists(_icon_src) and not os.path.exists(_icon_dst):
            try: shutil.copy2(_icon_src, _icon_dst)
            except: pass
        sync_code()
        threading.Thread(target=start_server, daemon=True).start()

    threading.Thread(target=_bg_init, daemon=True).start()
    app.mainloop()
