#!/bin/bash
# ============================================================
# 签到系统 macOS 安装包构建脚本
# 用法：./build_mac.sh
# ============================================================
set -e
cd "$(dirname "$0")"

echo "========================================="
echo "  签到系统 macOS 安装包构建"
echo "========================================="

# 清理旧构建
rm -rf build dist *.spec

echo "[1/3] PyInstaller 打包中..."
pyinstaller \
    --onedir \
    --name "签到系统" \
    --add-data "tablet:tablet" \
    --add-data "config.yaml:." \
    --hidden-import customtkinter \
    --hidden-import auth_manager \
    --hidden-import excel_manager \
    --hidden-import timer_manager \
    --hidden-import voice_broadcast \
    --hidden-import platform_utils \
    --hidden-import yaml \
    --clean \
    --noconfirm \
    desktop_app.py

echo ""
echo "[2/3] 创建启动脚本..."
cat > "dist/签到系统/start.sh" << 'STARTSCRIPT'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPYCACHEPREFIX="$HOME/.shuaka/pycache"
cd "$DIR"
open "签到系统.app"
STARTSCRIPT
chmod +x "dist/签到系统/start.sh"

echo "[3/3] 构建完成！"
echo ""
echo "  安装包位置: $(pwd)/dist/签到系统/"
echo "  应用位置:   $(pwd)/dist/签到系统/签到系统.app"
echo "  双击 start.sh 或直接打开 .app 即可运行"
echo ""
ls -la "dist/签到系统/"
