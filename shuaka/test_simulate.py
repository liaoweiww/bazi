#!/usr/bin/env python3
"""
读卡器模拟测试脚本
- 自动向系统输入模拟的身份证刷卡数据
- 用于验证 card_listener 的检测和解析功能

用法:
    1. 先在一个终端启动主程序: python main.py
    2. 在另一个终端运行此脚本: python test_simulate.py

注意: macOS 可能需要辅助功能权限
"""

import time
import sys
import random

# 模拟数据
TEST_NAMES = ["张三", "李四", "王五", "赵六", "孙七", "周八", "吴九"]
TEST_IDS = [
    "110101199001011234",
    "320102198506152345",
    "440103197912303456",
    "510104199508084567",
    "330105198203215678",
    "210106197611116789",
    "610107199909097890",
]

# 常见读卡器输出格式
FORMATS = [
    # 格式1: 姓名+身份证号 简单格式
    lambda n, i: f"{n} {i}",
    # 格式2: 带标签格式
    lambda n, i: f"姓名:{n}\n身份证号:{i}",
    # 格式3: 多行详细格式
    lambda n, i: f"姓名 {n}\n性别 男\n民族 汉\n出生 1990年1月1日\n住址 北京市\n身份证号 {i}",
]


def simulate_card_reader(text):
    """
    使用 AppleScript 模拟键盘输入
    适用于 macOS
    """
    import subprocess
    import shlex
    safe_text = text.replace('"', '\\"')
    script = f'''
    tell application "System Events"
        keystroke "{safe_text}"
    end tell
    '''
    # AppleScript 不适合大量文本，使用 pynput 替代
    pass


def simulate_with_pynput(text):
    """使用 pynput 模拟读卡器快速输入"""
    from pynput.keyboard import Controller
    keyboard = Controller()

    print(f"\n模拟刷卡数据: {repr(text)}")
    print("开始快速输入（模拟读卡器）...")

    # 模拟读卡器的快速输入（间隔 5-10ms）
    for char in text:
        keyboard.type(char)
        time.sleep(random.uniform(0.005, 0.015))  # 5-15ms 间隔

    print("输入完成！等待主程序检测...")
    time.sleep(2)


def main():
    print("读卡器模拟测试工具")
    print("=" * 40)
    print("请确保主程序已在另一个终端运行: python main.py")
    print()
    print("本脚本将模拟读卡器快速输入，验证主程序的检测功能。")
    print()

    try:
        from pynput.keyboard import Controller
    except ImportError:
        print("[错误] pynput 未安装: pip install pynput")
        sys.exit(1)

    mode = input("选择模式: (1) 单次测试 (2) 连续测试(3次) [默认1]: ").strip() or "1"

    count = 1 if mode == "1" else 3

    for i in range(count):
        if count > 1:
            print(f"\n=== 第 {i+1}/{count} 次测试 ===")
            time.sleep(1)

        name = TEST_NAMES[i % len(TEST_NAMES)]
        id_num = TEST_IDS[i % len(TEST_IDS)]
        fmt = random.choice(FORMATS)
        text = fmt(name, id_num)

        simulate_with_pynput(text)

    print("\n测试完成！请查看主程序终端输出是否成功捕获刷卡数据。")


if __name__ == "__main__":
    main()
