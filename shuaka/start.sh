#!/bin/bash
# ============================================================
# 签到系统启动脚本 (macOS)
# 用法：双击或终端执行 ./start.sh
# ============================================================
cd "$(dirname "$0")"

# 检查依赖，缺失则自动安装
python3 -c "import pynput" 2>/dev/null || {
    echo "[安装] 正在安装依赖包..."
    pip3 install -r requirements.txt -q
}

echo "[启动] 签到叫号系统..."

# 将 Python 字节码缓存重定向到本机目录，避免百度云跨平台同步冲突
export PYTHONPYCACHEPREFIX="$HOME/.shuaka/pycache"

python3 main.py "$@"
