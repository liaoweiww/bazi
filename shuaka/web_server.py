"""
本地 Web 服务器
- 平板叫号大屏页面
- 签到数据 JSON API
- 后台管理面板 (/admin) — 需登录
- 设置管理 + Logo 上传 — 需管理员权限
- 支持内网/外网双访问
"""

import os
import json
import time
import hmac
import hashlib
import socket
import secrets
import threading
from functools import wraps
from flask import Flask, jsonify, request, send_from_directory

# 路径常量
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TABLET_DIR = os.path.join(BASE_DIR, "tablet")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
USERS_FILE = os.path.join(BASE_DIR, "users.json")

os.makedirs(UPLOADS_DIR, exist_ok=True)

# Flask app
app = Flask(__name__, static_folder=TABLET_DIR, static_url_path="")
app.config["SECRET_KEY"] = secrets.token_hex(32)

# 全局引用
_excel_manager = None
_ngrok_url = None

# 登录令牌存储 {token: {username, role, expires}}
_sessions = {}


def set_excel_manager(mgr):
    global _excel_manager
    _excel_manager = mgr


def set_ngrok_url(url):
    global _ngrok_url
    _ngrok_url = url


# ---------- 用户管理 ----------

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"admin": {"password": "admin123", "role": "admin", "name": "管理员"}}


def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def check_auth(request):
    """验证请求的登录令牌，返回用户信息或 None"""
    token = request.headers.get("X-Auth-Token") or request.cookies.get("signin_token")
    if not token:
        return None
    session = _sessions.get(token)
    if not session:
        return None
    if time.time() > session["expires"]:
        del _sessions[token]
        return None
    return session


def require_auth(f):
    """装饰器：需要登录"""
    @wraps(f)
    def wrapper(*a, **kw):
        user = check_auth(request)
        if not user:
            return jsonify({"ok": False, "error": "请先登录"}), 401
        request.current_user = user
        return f(*a, **kw)
    return wrapper


def require_admin(f):
    """装饰器：需要管理员权限"""
    @wraps(f)
    def wrapper(*a, **kw):
        user = check_auth(request)
        if not user:
            return jsonify({"ok": False, "error": "请先登录"}), 401
        if user.get("role") != "admin":
            return jsonify({"ok": False, "error": "需要管理员权限"}), 403
        request.current_user = user
        return f(*a, **kw)
    return wrapper


# ---------- 登录 API ----------

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "无效请求"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    users = load_users()
    user = users.get(username)
    if not user or user.get("password") != password:
        return jsonify({"ok": False, "error": "用户名或密码错误"}), 401

    # 生成令牌
    token = secrets.token_hex(32)
    _sessions[token] = {
        "username": username,
        "role": user.get("role", "user"),
        "name": user.get("name", username),
        "expires": time.time() + 86400 * 7  # 7天有效
    }

    return jsonify({
        "ok": True,
        "token": token,
        "user": {"username": username, "role": user.get("role"), "name": user.get("name")}
    })


@app.route("/api/logout", methods=["POST"])
def api_logout():
    token = request.headers.get("X-Auth-Token") or request.cookies.get("signin_token")
    if token and token in _sessions:
        del _sessions[token]
    return jsonify({"ok": True})


@app.route("/api/me")
def api_me():
    user = check_auth(request)
    if not user:
        return jsonify({"ok": False}), 401
    return jsonify({"ok": True, "user": {
        "username": user["username"],
        "role": user["role"],
        "name": user["name"]
    }})


# ---------- 用户管理 API (管理员) ----------

@app.route("/api/users", methods=["GET"])
@require_admin
def api_list_users():
    users = load_users()
    result = {}
    for u, info in users.items():
        result[u] = {"role": info.get("role"), "name": info.get("name")}
    return jsonify({"ok": True, "users": result})


@app.route("/api/users", methods=["POST"])
@require_admin
def api_add_user():
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "无效数据"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    role = data.get("role", "user")

    if not username or not password:
        return jsonify({"ok": False, "error": "用户名和密码不能为空"}), 400

    users = load_users()
    if username in users:
        return jsonify({"ok": False, "error": "用户已存在"}), 400

    users[username] = {"password": password, "role": role, "name": data.get("name", username)}
    save_users(users)
    return jsonify({"ok": True})


@app.route("/api/users/<username>", methods=["DELETE"])
@require_admin
def api_delete_user(username):
    if username == "admin":
        return jsonify({"ok": False, "error": "不能删除admin账号"}), 400
    users = load_users()
    if username not in users:
        return jsonify({"ok": False, "error": "用户不存在"}), 404
    del users[username]
    save_users(users)
    return jsonify({"ok": True})


# ---------- 设置管理 ----------

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def deep_merge(base, override):
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


# ---------- 页面路由 ----------

@app.route("/")
def index():
    return send_from_directory(TABLET_DIR, "index.html")


@app.route("/login")
def login_page():
    return send_from_directory(TABLET_DIR, "login.html")


@app.route("/admin")
def admin_page():
    # admin.html 自己会检查登录状态，未登录跳转 /login
    return send_from_directory(TABLET_DIR, "admin.html")


# ---------- 数据 API（无需登录） ----------

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
@require_admin
def update_settings():
    data = request.get_json()
    if data:
        # 保护跑马灯：如果提交的 marquees 全是空的，保留原值不覆盖
        if "marquees" in data:
            mqs = data["marquees"]
            all_empty = all(
                not (m.get("enabled") and m.get("text", "").strip())
                for m in mqs
            )
            if all_empty:
                existing = load_settings()
                if existing.get("marquees"):
                    data["marquees"] = existing["marquees"]
        save_settings(data, merge=True)
        # 同步地点名到 Excel 管理器
        if "display" in data and "location" in data["display"] and data["display"]["location"]:
            global _excel_manager
            if _excel_manager:
                _excel_manager.location = data["display"]["location"]
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "无效数据"}), 400


# ---------- Logo 上传 ----------

@app.route("/api/upload/logo", methods=["POST"])
@require_admin
def upload_logo():
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "未选择文件"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"ok": False, "error": "文件名为空"}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"):
        return jsonify({"ok": False, "error": "仅支持 png/jpg/gif/webp/svg"}), 400

    filename = "logo" + ext
    filepath = os.path.join(UPLOADS_DIR, filename)

    for old_ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"):
        old_path = os.path.join(UPLOADS_DIR, "logo" + old_ext)
        if old_path != filepath and os.path.exists(old_path):
            os.remove(old_path)

    file.save(filepath)

    return jsonify({"ok": True, "logo_url": f"/uploads/{filename}"})


@app.route("/api/location", methods=["POST"])
@require_admin
def update_location():
    """更新签到地点"""
    data = request.get_json()
    if not data or "location" not in data:
        return jsonify({"ok": False, "error": "缺少location参数"}), 400
    global _excel_manager
    if _excel_manager:
        _excel_manager.location = data["location"]
    # 同时保存到 settings
    settings = load_settings()
    settings.setdefault("display", {})["location"] = data["location"]
    save_settings(settings, merge=False)
    return jsonify({"ok": True, "location": data["location"]})


@app.route("/api/manual_signin", methods=["POST"])
def manual_signin():
    """网页手动签到"""
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "无效数据"}), 400

    name = data.get("name", "").strip()
    id_number = data.get("id_number", "").strip() or "手动录入"
    if not name:
        return jsonify({"ok": False, "error": "请输入姓名"}), 400

    if _excel_manager is None:
        return jsonify({"ok": False, "error": "系统未就绪"}), 500

    from datetime import datetime
    record = _excel_manager.add_record(name, id_number)

    return jsonify({
        "ok": True,
        "record": record
    })


@app.route("/report")
def report_page():
    return send_from_directory(TABLET_DIR, "report.html")


# ---------- 数据统计 API ----------

@app.route("/api/stats")
def api_stats():
    """签到统计报表"""
    if _excel_manager is None:
        return jsonify({})
    period = request.args.get("period", "week")
    records = _excel_manager.get_all_records()

    from datetime import datetime, timedelta
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    result = {
        "total": len(records),
        "today": len([r for r in records if r["sign_time"].startswith(today)]),
        "location": _excel_manager.location if _excel_manager else "",
    }

    # 本周/本月
    monday = now - timedelta(days=now.weekday())
    result["this_week"] = len([r for r in records if r["sign_time"] >= monday.strftime("%Y-%m-%d")])
    result["this_month"] = len([r for r in records if r["sign_time"][:7] == now.strftime("%Y-%m")])

    # 按周期聚合
    labels, values = [], []
    if period == "day":
        for i in range(6, -1, -1):
            d = (now - timedelta(days=i)).strftime("%m-%d")
            cnt = len([r for r in records if r["sign_time"].startswith((now - timedelta(days=i)).strftime("%Y-%m-%d"))])
            labels.append(d); values.append(cnt)
    elif period == "month":
        for i in range(5, -1, -1):
            ym = (now.replace(day=1) - timedelta(days=i*30)).strftime("%Y-%m")
            cnt = len([r for r in records if r["sign_time"][:7] == ym])
            labels.append(ym); values.append(cnt)
    else:  # week
        weekdays = ["周一","周二","周三","周四","周五","周六","周日"]
        for i in range(6, -1, -1):
            d = (now - timedelta(days=i))
            cnt = len([r for r in records if r["sign_time"].startswith(d.strftime("%Y-%m-%d"))])
            labels.append(weekdays[d.weekday()]); values.append(cnt)

    result["labels"] = labels
    result["values"] = values

    # 时段分布
    hour_dist = {}
    for r in records:
        try:
            h = r["sign_time"][11:13]
            hour_dist[h] = hour_dist.get(h, 0) + 1
        except: pass
    result["hourly"] = [{"hour": int(h), "count": c} for h, c in sorted(hour_dist.items())]

    # 状态分布
    status_dist = {"正常等待": 0, "即将超时": 0, "已超时": 0}
    warn_min = load_settings().get("timer", {}).get("warning_minutes", 35)
    over_min = load_settings().get("timer", {}).get("remind_minutes", 40)
    for r in records:
        try:
            t = datetime.strptime(r["sign_time"], "%Y-%m-%d %H:%M:%S")
            waited = (now - t).total_seconds() / 60
            if waited >= over_min: status_dist["已超时"] += 1
            elif waited >= warn_min: status_dist["即将超时"] += 1
            else: status_dist["正常等待"] += 1
        except: pass
    result["status_dist"] = {k: v for k, v in status_dist.items() if v > 0}

    # 地点分布
    loc_dist = {}
    for r in records:
        loc = r.get("location", "未知")
        loc_dist[loc] = loc_dist.get(loc, 0) + 1
    result["location_dist"] = loc_dist

    return jsonify(result)


# ---------- 清除签到记录 ----------

@app.route("/api/clear_records", methods=["POST"])
@require_admin
def clear_records():
    """清除签到记录"""
    if _excel_manager is None:
        return jsonify({"ok": False, "error": "系统未就绪"}), 500

    data = request.get_json() or {}
    mode = data.get("mode", "today")

    import glob
    excel_dir = _excel_manager.excel_dir

    if mode == "all":
        for f in glob.glob(os.path.join(excel_dir, "签到记录_*.xlsx")):
            try: os.remove(f)
            except: pass
        # 清内存缓存
        _excel_manager._records_cache = []
        return jsonify({"ok": True, "message": "已清除全部签到记录"})

    # 只清今天
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    all_recs = _excel_manager.get_all_records()
    keep = [r for r in all_recs if not r["sign_time"].startswith(today)]
    removed = len(all_recs) - len(keep)

    # 重建所有 Excel 文件
    for f in glob.glob(os.path.join(excel_dir, "签到记录_*.xlsx")):
        try: os.remove(f)
        except: pass

    # 按原地点分组写回
    groups = {}
    for r in keep:
        groups.setdefault(r.get("location", "未知"), []).append(r)

    orig_loc = _excel_manager.location
    try:
        for loc, recs in groups.items():
            _excel_manager.location = loc
            for r in recs:
                t = datetime.strptime(r["sign_time"], "%Y-%m-%d %H:%M:%S")
                _excel_manager.add_record(r["name"], r["id_number"], t, r.get("status","等待中"), {"_recalled": r.get("_recalled",0)}, _rebuild=True)
    finally:
        _excel_manager.location = orig_loc

    _excel_manager._records_cache = keep
    return jsonify({"ok": True, "message": f"已清除今日 {removed} 条记录"})


# ---------- 删除/编辑记录 ----------

@app.route("/api/delete_records", methods=["POST"])
def delete_records():
    """删除指定签到记录"""
    if _excel_manager is None:
        return jsonify({"ok": False, "error": "系统未就绪"}), 500
    data = request.get_json() or {}
    targets = data.get("targets", [])  # [{seq, location}, ...]
    if not targets:
        return jsonify({"ok": False, "error": "请指定要删除的记录"}), 400

    import glob
    all_recs = _excel_manager.get_all_records()
    target_set = set()
    for t in targets:
        target_set.add((t.get("seq"), t.get("location", "")))

    keep = [r for r in all_recs if (r.get("seq"), r.get("location", "")) not in target_set]
    removed = len(all_recs) - len(keep)

    # 重建 Excel
    excel_dir = _excel_manager.excel_dir
    for f in glob.glob(os.path.join(excel_dir, "签到记录_*.xlsx")):
        try: os.remove(f)
        except Exception: pass

    groups = {}
    for r in keep:
        groups.setdefault(r.get("location", "未知"), []).append(r)

    orig_loc = _excel_manager.location
    from datetime import datetime
    try:
        for loc, recs in groups.items():
            _excel_manager.location = loc
            for r in recs:
                t = datetime.strptime(r["sign_time"], "%Y-%m-%d %H:%M:%S")
                _excel_manager.add_record(r["name"], r["id_number"], t, r.get("status","等待中"), {"_recalled": r.get("_recalled",0)}, _rebuild=True)
    finally:
        _excel_manager.location = orig_loc

    _excel_manager._records_cache = keep
    return jsonify({"ok": True, "message": f"已删除 {removed} 条记录", "removed": removed})


@app.route("/api/update_record", methods=["POST"])
def update_record():
    """编辑签到记录"""
    if _excel_manager is None:
        return jsonify({"ok": False, "error": "系统未就绪"}), 500
    data = request.get_json() or {}
    seq = data.get("seq")
    location = data.get("location", "")
    new_name = data.get("name", "").strip()
    new_id = data.get("id_number", "").strip()
    new_status = data.get("_set_status", "").strip()
    recalled = data.get("_recalled")

    if not seq:
        return jsonify({"ok": False, "error": "缺少必要参数"}), 400

    # 修改内存缓存
    for r in _excel_manager._records_cache:
        if r.get("seq") == seq and r.get("location", "") == location:
            if new_name: r["name"] = new_name
            if new_id: r["id_number"] = new_id
            if new_status: r["status"] = new_status
            if recalled is not None: r["_recalled"] = recalled
            break

    # 重建 Excel
    import glob
    excel_dir = _excel_manager.excel_dir
    all_recs = _excel_manager._records_cache

    for f in glob.glob(os.path.join(excel_dir, "签到记录_*.xlsx")):
        try: os.remove(f)
        except Exception: pass

    groups = {}
    for r in all_recs:
        groups.setdefault(r.get("location", "未知"), []).append(r)

    orig_loc = _excel_manager.location
    from datetime import datetime
    try:
        for loc, recs in groups.items():
            _excel_manager.location = loc
            for r in recs:
                t = datetime.strptime(r["sign_time"], "%Y-%m-%d %H:%M:%S")
                _excel_manager.add_record(r["name"], r["id_number"], t, r.get("status","等待中"), {"_recalled": r.get("_recalled",0)}, _rebuild=True)
    finally:
        _excel_manager.location = orig_loc

    return jsonify({"ok": True, "message": "记录已更新"})


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
    print(f"  默认账号: admin / admin123")
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
