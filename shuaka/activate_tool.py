"""
独立激活工具 GUI — Windows 双击运行
显示机器码，支持时效授权码 (1/6/12个月)
"""
import os
import sys
import json
import hmac
import hashlib
import socket
import time
import uuid as _uuid
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

_SECRET = b"shuaka@2026!license_key_internal_use_only"

WIDTH = 460
HEIGHT = 440
FONT = ("Microsoft YaHei", 10)
FONT_BOLD = ("Microsoft YaHei", 10, "bold")
FONT_CODE = ("Consolas", 11, "bold")
FONT_TITLE = ("Microsoft YaHei", 13, "bold")
BG = "#f5f6f8"
CARD_BG = "#ffffff"
ACCENT = "#4f6ef7"
TEXT = "#1a1a2e"
TEXT2 = "#6b7280"
GREEN = "#10b981"
RED = "#ef4444"
WARN = "#f59e0b"
BORDER = "#e5e7eb"


def _get_machine_file():
    if os.name == 'nt':
        local_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'shuaka')
    else:
        local_dir = os.path.join(os.path.expanduser('~'), '.shuaka')
    os.makedirs(local_dir, exist_ok=True)
    return os.path.join(local_dir, 'machine.json')


def get_machine_code():
    parts = [socket.gethostname()]
    try:
        node = _uuid.getnode()
        parts.append(format(node, 'x'))
    except Exception:
        pass
    raw = "|".join(parts)
    h = hashlib.sha256(raw.encode()).hexdigest()[:16].upper()
    return "-".join([h[i:i+4] for i in range(0, 16, 4)])


def generate_license(machine_code, months):
    code = machine_code.replace("-", "").upper()
    expiry = (datetime.now() + timedelta(days=months * 30)).strftime("%Y%m%d")
    payload = f"{code}|{expiry}"
    sig = hmac.new(_SECRET, payload.encode(), hashlib.sha256).hexdigest()[:16].upper()
    lic = "-".join([sig[i:i+4] for i in range(0, 16, 4)])
    return lic, expiry


def verify_license(license_code, expiry_str):
    mc = get_machine_code()
    code = mc.replace("-", "").upper()
    payload = f"{code}|{expiry_str}"
    sig = hmac.new(_SECRET, payload.encode(), hashlib.sha256).hexdigest()[:16].upper()
    expected = "-".join([sig[i:i+4] for i in range(0, 16, 4)])
    return license_code.replace("-", "").upper() == expected.replace("-", "").upper()


def save_license(license_code, expiry_str):
    mf = _get_machine_file()
    existing = {}
    if os.path.exists(mf):
        with open(mf, "r", encoding="utf-8") as f:
            existing = json.load(f)
    existing["license"] = license_code.strip()
    existing["expiry"] = expiry_str.strip()
    with open(mf, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)


def load_license_info():
    mf = _get_machine_file()
    if not os.path.exists(mf):
        return None
    try:
        with open(mf, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("license", ""), data.get("expiry", "")
    except Exception:
        return None


class ActivateApp:
    def __init__(self, root):
        self.root = root
        root.title("身份证签到系统 — 激活工具")
        root.geometry(f"{WIDTH}x{HEIGHT}")
        root.resizable(False, False)
        root.configure(bg=BG)
        root.update_idletasks()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = (sw - WIDTH) // 2
        y = (sh - HEIGHT) // 2
        root.geometry(f"+{x}+{y}")
        self._build()
        self._check_existing()

    def _check_existing(self):
        info = load_license_info()
        if info:
            lic, exp = info
            mc = get_machine_code()
            if verify_license(lic, exp):
                try:
                    expiry_date = datetime.strptime(exp, "%Y%m%d")
                    days = (expiry_date - datetime.now()).days
                    if days > 0:
                        self.status.config(
                            text=f"已激活 · 有效期至 {exp[:4]}-{exp[4:6]}-{exp[6:8]} · 剩余 {days} 天",
                            fg=GREEN if days > 30 else WARN)
                        self.btn.config(text="已激活", state="disabled", bg=GREEN)
                        return
                    else:
                        self.status.config(text="授权已过期，请重新激活", fg=RED)
                except Exception:
                    pass
        self.status.config(text="未激活，请输入管理员提供的授权码", fg=TEXT2)

    def _build(self):
        tk.Label(self.root, text="软件激活", font=FONT_TITLE, fg=TEXT, bg=BG).pack(pady=(28, 4))
        tk.Label(self.root, text="输入管理员提供的授权码以激活系统",
                 font=FONT, fg=TEXT2, bg=BG).pack(pady=(0, 16))

        # 机器码卡片
        card = tk.Frame(self.root, bg=CARD_BG, highlightthickness=1,
                        highlightbackground=BORDER, highlightcolor=BORDER)
        card.place(x=24, y=100, width=WIDTH-48, height=84)
        tk.Label(card, text="本机机器码", font=FONT, fg=TEXT2, bg=CARD_BG).pack(pady=(12, 2))
        tk.Label(card, text=get_machine_code(), font=FONT_CODE, fg=ACCENT, bg=CARD_BG).pack()
        tk.Label(card, text="将机器码发送给管理员以获取授权码",
                 font=("Microsoft YaHei", 8), fg=TEXT2, bg=CARD_BG).pack(pady=(4, 0))

        # 有效期选择
        dur_frame = tk.Frame(self.root, bg=BG)
        dur_frame.place(x=24, y=196, width=WIDTH-48, height=30)
        tk.Label(dur_frame, text="有效期:", font=FONT, fg=TEXT2, bg=BG).pack(side="left")
        self.months_var = tk.IntVar(value=12)
        for m, txt in [(1, "1个月"), (6, "6个月"), (12, "12个月")]:
            tk.Radiobutton(dur_frame, text=txt, variable=self.months_var, value=m,
                           font=("Microsoft YaHei", 9), bg=BG, fg=TEXT,
                           activebackground=BG, selectcolor=BG,
                           command=self._on_month_change).pack(side="left", padx=(10, 0))

        # 只读的授权码显示（生成后显示）
        self.gen_frame = tk.Frame(self.root, bg=CARD_BG, highlightthickness=1,
                                  highlightbackground=BORDER)
        self.gen_frame.place(x=24, y=234, width=WIDTH-48, height=60)
        tk.Label(self.gen_frame, text="生成的授权码", font=FONT, fg=TEXT2, bg=CARD_BG).pack(pady=(8, 2))
        self.gen_label = tk.Label(self.gen_frame, text="--", font=FONT_CODE, fg=ACCENT, bg=CARD_BG)
        self.gen_label.pack()
        self.gen_frame.pack_forget()  # 用户端隐藏（只有开发者面板用到）

        # 输入框
        self.entry_var = tk.StringVar()
        entry = tk.Entry(self.root, textvariable=self.entry_var, font=FONT_CODE,
                         justify="center", relief="solid", bd=1, bg="#ffffff", fg=TEXT)
        entry.place(x=24, y=240, width=WIDTH-48, height=40)
        self._placeholder = "XXXX-XXXX-XXXX-XXXX-YYYYMMDD"
        self.entry_var.set(self._placeholder)
        entry.config(fg=TEXT2)
        entry.bind("<FocusIn>", self._on_focus_in)
        entry.bind("<FocusOut>", self._on_focus_out)

        # 按钮
        self.btn = tk.Button(self.root, text="激  活", font=FONT_BOLD,
                             bg=ACCENT, fg="#ffffff", relief="flat",
                             activebackground="#3d5ce5", activeforeground="#ffffff",
                             cursor="hand2", command=self._activate)
        self.btn.place(x=24, y=296, width=WIDTH-48, height=42)

        # 开发者模式：显示机器码并生成授权码
        dev_btn = tk.Button(self.root, text="开发者: 生成授权码", font=("Microsoft YaHei", 8),
                            bg="#e5e7eb", fg=TEXT2, relief="flat", cursor="hand2",
                            command=self._show_dev)
        dev_btn.place(x=WIDTH//2-60, y=352, width=120, height=24)

        self.status = tk.Label(self.root, text="", font=FONT, bg=BG, fg=TEXT2, wraplength=WIDTH-60)
        self.status.place(x=24, y=380, width=WIDTH-48, height=36)

    def _on_focus_in(self, e):
        if self.entry_var.get() == self._placeholder:
            self.entry_var.set("")
            e.widget.config(fg=TEXT)

    def _on_focus_out(self, e):
        if not self.entry_var.get().strip():
            self.entry_var.set(self._placeholder)
            e.widget.config(fg=TEXT2)

    def _on_month_change(self):
        pass

    def _show_dev(self):
        mc = get_machine_code()
        months = self.months_var.get()
        lic, expiry = generate_license(mc, months)
        full = f"{lic}-{expiry}"
        self.entry_var.set(full)
        for w in self.root.winfo_children():
            if isinstance(w, tk.Entry):
                w.config(fg=TEXT)
        self.status.config(
            text=f"已生成 · 有效期 {expiry[:4]}-{expiry[4:6]}-{expiry[6:8]} ({months}个月) · 请复制授权码",
            fg=ACCENT)

    def _activate(self):
        raw = self.entry_var.get().strip()
        if raw == self._placeholder or not raw:
            self.status.config(text="请输入授权码", fg=RED)
            return

        # 解析组合格式: XXXX-XXXX-XXXX-XXXX-YYYYMMDD
        parts = raw.replace("-", " ").split()
        if len(parts) >= 5 and len(parts[4]) == 8:
            code = "-".join(parts[:4])
            expiry = parts[4]
        else:
            self.status.config(text="格式错误，应为: XXXX-XXXX-XXXX-XXXX-YYYYMMDD", fg=RED)
            return

        if len(code.replace("-", "")) != 16:
            self.status.config(text="授权码 HMAC 部分应为 16 位", fg=RED)
            return

        self.btn.config(text="验证中...", state="disabled")
        self.root.update()

        if verify_license(code, expiry):
            save_license(code, expiry)
            try:
                expiry_date = datetime.strptime(expiry, "%Y%m%d")
                days = (expiry_date - datetime.now()).days
                self.status.config(
                    text=f"✓ 激活成功！有效期至 {expiry[:4]}-{expiry[4:6]}-{expiry[6:8]} · 剩余 {days} 天",
                    fg=GREEN)
            except Exception:
                self.status.config(text="✓ 激活成功！", fg=GREEN)
            self.btn.config(text="激活成功", state="disabled", bg=GREEN)
            messagebox.showinfo("激活成功", "授权已生效，软件可正常使用。")
        else:
            self.status.config(text="✗ 授权码无效，请检查后重试", fg=RED)
            self.btn.config(text="激  活", state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = ActivateApp(root)
    root.mainloop()
