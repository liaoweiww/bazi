#!/bin/bash
# ============================================================
# 签到系统一键安装脚本 (macOS)
# 用法：终端执行 ./install.sh
# ============================================================

set -e

cd "$(dirname "$0")"

echo ""
echo "==========================================="
echo "  签到叫号系统 - macOS 安装"
echo "==========================================="

# 检查 Python3
if ! command -v python3 &>/dev/null; then
    echo ""
    echo "  ✗ 未检测到 Python 3"
    echo "  请先安装 Python: https://python.org"
    echo "  或通过 Homebrew: brew install python3"
    exit 1
fi

echo "  ✓ 检测到 $(python3 --version)"

# 运行安装程序
python3 install.py

echo ""
echo "安装脚本执行完毕。"
