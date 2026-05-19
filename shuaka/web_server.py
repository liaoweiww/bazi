"""
本地 Web 服务器
- 平板叫号大屏页面
- 签到数据 JSON API
- 后台管理面板 (/admin)
- 设置管理 + Logo 上传
- 支持内网/外网双访问
"""

import os
import json
import socket
import threading
from flask import Flask, jsonify, request, send_from_directory

# 路径常量
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TABLET_DIR = os.path.join(BASE_DIR, "tablet")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

os.makedirs(UPLOADS_DIR, exist_ok=True)

# Flask app
app = Flask(__name__, static_folder=TABLET_DIR, static_url_path="")

# 全局引用
_excel_manager = None
_ngrok_url = None


def set_excel_manager(mgr):
    global _excel_manager
    _excel_manager = mgr


def set_ngrok_url(url):
    global _ngrok_url
    _ngrok_url = url


# ---------- 设置管理 ----------

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def deep_merge(base, override):
    """深度合并两个字典，override 覆盖 base"""
    result = base.copy()
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def save_settings(data, merge=True):
    if merge:
        existing = load_settings()
        data = deep_merge(existing, data)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------- 大屏页面 ----------

@app.route("/")
def index():
    return send_from_directory(TABLET_DIR, "index.html")


@app.route("/admin")
def admin():
    return send_from_directory(TABLET_DIR, "admin.html")


# ---------- 数据 API ----------

@app.route("/api/signins")
def api_signins():
    if _excel_manager is None:
        return jsonify([])
    return jsonify(_excel_manager.get_all_records())


@app.route("/api/status")
def api_status():
    if _excel_manager is None:
        return jsonify({"status": "未就绪", "record_count": 0})
    return jsonify({
        "status": "运行中",
        "record_count": len(_excel_manager.get_all_records()),
        "today_count": len(_excel_manager.get_today_records()),
        "ngrok_url": _ngrok_url
    })


# ---------- 设置 API ----------

@app.route("/api/settings", methods=["GET"])
def get_settings():
    return jsonify(load_settings())


@app.route("/api/settings", methods=["POST"])
def update_settings():
    data = request.get_json()
    if data:
        save_settings(data, merge=True)
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "无效数据"}), 400


# ---------- Logo 上传 ----------

@app.route("/api/upload/logo", methods=["POST"])
def upload_logo():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "未选择文件"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"ok": False, "error": "文件名为空"}), 400

    # 检查文件类型
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"):
        return jsonify({"ok": False, "error": "仅支持 png/jpg/gif/webp/svg"}), 400

    # 保存
    filename = "logo" + ext
    filepath = os.path.join(UPLOADS_DIR, filename)

    # 清理旧 logo
    for old_ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"):
        old_path = os.path.join(UPLOADS_DIR, "logo" + old_ext)
        if old_path != filepath and os.path.exists(old_path):
            os.remove(old_path)

    file.save(filepath)

    logo_url = f"/uploads/{filename}"
    return jsonify({"ok": True, "logo_url": logo_url})


@app.route("/uploads/<filename>")
def serve_upload(filename):
    return send_from_directory(UPLOADS_DIR, filename)


# ---------- 网络工具 ----------

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(("10.254.254.254", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_all_ips():
    """获取本机所有 IP 地址"""
    ips = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None):
            ip = info[4][0]
            if not ip.startswith("127.") and ":" not in ip:
                ips.add(ip)
    except Exception:
        pass
    ips.add(get_local_ip())
    return sorted(ips)


def start_server(host="0.0.0.0", port=5002):
    local_ip = get_local_ip()
    all_ips = get_all_ips()

    print(f"\n{'='*55}")
    print(f"  叫号大屏 Web 服务器已启动")
    print(f"  管理后台: http://{local_ip}:{port}/admin")
    print(f"  大屏展示: http://{local_ip}:{port}/")
    print(f"  {'─'*45}")
    print(f"  内网访问地址:")
    for ip in all_ips:
        print(f"    http://{ip}:{port}")
    if _ngrok_url:
        print(f"  {'─'*45}")
        print(f"  外网访问地址: {_ngrok_url}")
    print(f"{'='*55}\n")

    t = threading.Thread(
        target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False),
        daemon=True
    )
    t.start()
    return t
