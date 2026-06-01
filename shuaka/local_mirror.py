"""
本地安全镜像模块
每次数据变更时自动将 BaiduSyncdisk 中的关键数据镜像到本地目录，
防止云同步目录误删导致数据丢失。

安全规则：
- 源数据有效（非空）时才镜像到本地
- 源数据缺失或损坏时，跳过镜像，保留本地副本
- 启动时如果 BaiduSyncdisk 为空但 local_backup 有数据，自动恢复
"""

import os
import shutil
import glob
import logging

logger = logging.getLogger("signin")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_BACKUP = os.path.join(BASE_DIR, "local_backup")
SYNC_ROOT = os.path.join(BASE_DIR, "BaiduSyncdisk")


def ensure_dirs():
    """确保所有数据目录存在"""
    for d in ["签到记录", "备份", "回收站", "uploads", "events"]:
        os.makedirs(os.path.join(SYNC_ROOT, d), exist_ok=True)
    for d in ["签到记录"]:
        os.makedirs(os.path.join(LOCAL_BACKUP, d), exist_ok=True)


def mirror_critical_data(kind="all"):
    """
    将 BaiduSyncdisk 中的关键数据镜像到 local_backup/
    仅在源数据有效时执行镜像，避免用空数据覆盖本地备份。

    kind: "all" | "excel" | "settings" | "users"
    """
    try:
        if kind in ("all", "excel"):
            _mirror_excel()

        if kind in ("all", "settings"):
            _mirror_file("settings.json")

        if kind in ("all", "users"):
            _mirror_file("users.json")

    except Exception:
        pass


def restore_from_local():
    """
    如果 BaiduSyncdisk 数据缺失，从 local_backup 恢复。
    在系统启动时调用，防止云同步误删导致数据丢失。
    """
    restored = False
    try:
        src_excel = os.path.join(SYNC_ROOT, "签到记录")
        bak_excel = os.path.join(LOCAL_BACKUP, "签到记录")

        # 检查 BaiduSyncdisk 是否缺失签到数据
        excel_files = glob.glob(os.path.join(src_excel, "签到记录_*.xlsx"))
        bak_files = glob.glob(os.path.join(bak_excel, "签到记录_*.xlsx"))

        if not excel_files and bak_files:
            logger.warning("[数据保护] BaiduSyncdisk 签到数据缺失，从本地备份恢复...")
            os.makedirs(src_excel, exist_ok=True)
            for fp in bak_files:
                shutil.copy2(fp, os.path.join(src_excel, os.path.basename(fp)))
            restored = True

        # 检查 settings.json
        src_s = os.path.join(SYNC_ROOT, "settings.json")
        bak_s = os.path.join(LOCAL_BACKUP, "settings.json")
        if (not os.path.isfile(src_s) or os.path.getsize(src_s) < 10) and os.path.isfile(bak_s) and os.path.getsize(bak_s) >= 10:
            logger.warning("[数据保护] BaiduSyncdisk settings.json 缺失，从本地备份恢复...")
            shutil.copy2(bak_s, src_s)
            restored = True

        # 检查 users.json
        src_u = os.path.join(SYNC_ROOT, "users.json")
        bak_u = os.path.join(LOCAL_BACKUP, "users.json")
        if (not os.path.isfile(src_u) or os.path.getsize(src_u) < 10) and os.path.isfile(bak_u) and os.path.getsize(bak_u) >= 10:
            logger.warning("[数据保护] BaiduSyncdisk users.json 缺失，从本地备份恢复...")
            shutil.copy2(bak_u, src_u)
            restored = True

    except Exception as e:
        logger.warning(f"[数据保护] 恢复失败: {e}")

    return restored


def _mirror_excel():
    src_dir = os.path.join(SYNC_ROOT, "签到记录")
    dst_dir = os.path.join(LOCAL_BACKUP, "签到记录")

    if not os.path.isdir(src_dir):
        return
    os.makedirs(dst_dir, exist_ok=True)

    for fp in glob.glob(os.path.join(src_dir, "签到记录_*.xlsx")):
        # 安全检查：源文件必须大于 1KB 才镜像（避免覆盖本地有效数据）
        if os.path.getsize(fp) < 1024:
            continue
        dst = os.path.join(dst_dir, os.path.basename(fp))
        try:
            shutil.copy2(fp, dst)
        except Exception:
            pass


def _mirror_file(filename):
    src = os.path.join(SYNC_ROOT, filename)
    dst = os.path.join(LOCAL_BACKUP, filename)

    if not os.path.isfile(src):
        return
    # 安全检查：源文件必须大于 10 字节才镜像
    if os.path.getsize(src) < 10:
        return
    os.makedirs(LOCAL_BACKUP, exist_ok=True)

    try:
        shutil.copy2(src, dst)
    except Exception:
        pass
