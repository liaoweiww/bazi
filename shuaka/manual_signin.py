#!/usr/bin/env python3
"""
手动签到工具
- 用于无读卡器时手动录入签到
- 也可用于测试系统功能
用法: python manual_signin.py
"""

import sys
import os
import re
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from excel_manager import ExcelManager
from voice_broadcast import VoiceBroadcaster
import yaml


def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_id(id_number):
    """简单的身份证号格式校验"""
    if not re.match(r'^\d{17}[\dXx]$', id_number):
        return False
    return True


def main():
    config = load_config()
    location = config.get("location", "默认地点")
    excel_dir = config.get("excel_dir", "./签到记录")
    voice_cfg = config.get("voice", {})

    excel_mgr = ExcelManager(excel_dir, location)
    voice = VoiceBroadcaster(voice_cfg)
    voice.start()

    print("=" * 40)
    print("  手动签到录入")
    print(f"  地点: {location}")
    print("  输入 'q' 退出")
    print("=" * 40)

    while True:
        print()
        name = input("姓名: ").strip()
        if name.lower() == 'q':
            break
        if not name:
            print("姓名不能为空")
            continue

        id_number = input("身份证号: ").strip()
        if id_number.lower() == 'q':
            break

        if not validate_id(id_number):
            print("⚠️ 身份证号格式不正确（应为18位），仍将记录。")

        record = excel_mgr.add_record(name, id_number)
        voice.welcome(name)
        print(f"✅ 签到成功！序号: {record['seq']}，时间: {record['sign_time']}")

    voice.stop()
    print("已退出手动签到。")


if __name__ == "__main__":
    main()
