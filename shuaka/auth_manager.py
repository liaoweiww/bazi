"""
授权管理 — 硬件绑定 + 时效授权码
- 机器指纹: MAC地址 + 主机名 SHA256
- 授权码: HMAC-SHA256(机器码 + 过期时间)
- 支持 1/6/12 个月有效期
"""
import os
import json
import hmac
import hashlib
import socket
import time
import uuid as _uuid
from datetime import datetime, timedelta

_SECRET = b"shuaka@2026!license_key_internal_use_only"


def _get_machine_file():
    if os.name == 'nt':
        local_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'shuaka')
    else:
        local_dir = os.path.join(os.path.expanduser('~'), '.shuaka')
    os.makedirs(local_dir, exist_ok=True)
    return os.path.join(local_dir, 'machine.json')


def get_machine_code():
    """生成机器指纹"""
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
    """
    根据机器码 + 有效期(月) 生成授权码
    签名内容: machine_code | expiry_date
    """
    code = machine_code.replace("-", "").upper()
    expiry = (datetime.now() + timedelta(days=months * 30)).strftime("%Y%m%d")
    payload = f"{code}|{expiry}"
    sig = hmac.new(_SECRET, payload.encode(), hashlib.sha256).hexdigest()[:16].upper()
    lic = "-".join([sig[i:i+4] for i in range(0, 16, 4)])
    return lic, expiry


def verify_license(license_code, expiry_str):
    """验证授权码是否匹配本机 + 有效期"""
    mc = get_machine_code()
    code = mc.replace("-", "").upper()
    payload = f"{code}|{expiry_str}"
    sig = hmac.new(_SECRET, payload.encode(), hashlib.sha256).hexdigest()[:16].upper()
    expected = "-".join([sig[i:i+4] for i in range(0, 16, 4)])
    return license_code.replace("-", "").upper() == expected.replace("-", "").upper()


def _is_expired(expiry_str):
    """检查是否过期"""
    try:
        expiry_date = datetime.strptime(expiry_str, "%Y%m%d")
        return datetime.now() > expiry_date
    except Exception:
        return True


def get_license_info():
    """获取当前授权信息"""
    mf = _get_machine_file()
    if not os.path.exists(mf):
        return {"activated": False, "machine_code": get_machine_code()}
    try:
        with open(mf, "r", encoding="utf-8") as f:
            data = json.load(f)
        lic = data.get("license", "")
        exp = data.get("expiry", "")
        if not lic or not exp:
            return {"activated": False, "machine_code": get_machine_code()}
        valid = verify_license(lic, exp)
        expired = _is_expired(exp) if valid else False
        expiry_display = f"{exp[:4]}-{exp[4:6]}-{exp[6:8]}" if exp else ""
        return {
            "activated": valid and not expired,
            "machine_code": get_machine_code(),
            "expiry": expiry_display,
            "expired": expired,
            "days_left": (datetime.strptime(exp, "%Y%m%d") - datetime.now()).days if valid else 0,
        }
    except Exception:
        return {"activated": False, "machine_code": get_machine_code()}


def is_activated():
    """检查是否已激活且未过期"""
    info = get_license_info()
    return info.get("activated", False)


def save_license(license_code, expiry_str):
    """保存授权码和有效期到 machine.json"""
    mf = _get_machine_file()
    existing = {}
    if os.path.exists(mf):
        with open(mf, "r", encoding="utf-8") as f:
            existing = json.load(f)
    existing["license"] = license_code.strip()
    existing["expiry"] = expiry_str.strip()
    with open(mf, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
