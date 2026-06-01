"""
Windows 签到系统启动管理器
- 双击运行，无需管理员权限（Raw Input API）
- 从 Mac SMB 同步最新代码
- --service: 直接启动服务模式
"""
import os, sys, time, json, shutil, socket, subprocess, threading

LOCAL_DIR = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'shuaka')

def get_source_dir():
    my_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    if my_dir.startswith('\\\\'): return my_dir
    unc = r'\\192.168.50.226\shuaka'
    return unc if os.path.exists(os.path.join(unc, 'main.py')) else my_dir

def sync_code():
    src = get_source_dir()
    print(f'[同步] {src} → {LOCAL_DIR}')
    try:
        # 专门同步 .py 文件（copytree 在某些环境下不会覆盖）
        os.makedirs(LOCAL_DIR, exist_ok=True)
        for fn in os.listdir(src):
            if fn.endswith('.py') or fn.endswith('.dll') or fn.endswith('.ini') or fn.endswith('.bat') or fn in ('config.yaml', 'VERSION'):
                sp = os.path.join(src, fn)
                dp = os.path.join(LOCAL_DIR, fn)
                if os.path.isfile(sp):
                    shutil.copy2(sp, dp)
        # tablet 目录
        ts = os.path.join(src, 'tablet')
        td = os.path.join(LOCAL_DIR, 'tablet')
        if os.path.isdir(ts):
            os.makedirs(td, exist_ok=True)
            for fn in os.listdir(ts):
                sf = os.path.join(ts, fn)
                df = os.path.join(td, fn)
                if os.path.isfile(sf):
                    shutil.copy2(sf, df)
        print('[同步] 完成')
        return True
    except Exception as e:
        print(f'[同步] 失败: {e}')
        return os.path.exists(os.path.join(LOCAL_DIR, 'main.py'))

def is_port_open(port=5002):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(1)
        r = s.connect_ex(('127.0.0.1', port)); s.close()
        return r == 0
    except: return False

def show_status():
    running = is_port_open()
    card_ok = False
    if running:
        try:
            import urllib.request
            resp = urllib.request.urlopen('http://127.0.0.1:5002/api/monitor', timeout=2)
            data = json.loads(resp.read())
            cr = data.get('card_reader', {})
            card_ok = cr.get('online', False)
        except: pass
    print(f'\n{"="*50}')
    print(f'  服务: {"🟢 运行中" if running else "🔴 未运行"}')
    print(f'  读卡器: {"🟢 在线" if card_ok else ("⚪ 未启用" if running else "--")}')
    print(f'  地址: http://127.0.0.1:5002')
    print(f'  后台: http://127.0.0.1:5002/admin')
    print(f'{"="*50}\n')

def main_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('''
╔══════════════════════════════════════════╗
║     身份证签到系统 - Windows 启动管理器   ║
╠══════════════════════════════════════════╣
║   [1] 🚀 启动服务                        ║
║   [2] 🔄 重启服务                        ║
║   [3] 🛑 停止服务                        ║
║   [4] 📡 同步代码                        ║
║   [5] 🌐 打开大屏                        ║
║   [6] ⚙ 管理后台                        ║
║   [0] 退出                               ║
╚══════════════════════════════════════════╝''')
    show_status()
    choice = input('请选择 [1]: ').strip() or '1'

    if choice == '1':
        if is_port_open(5002): print('服务已在运行'); time.sleep(1); return True
        sync_code()
        print('[启动] 正在启动...')
        os.chdir(LOCAL_DIR); sys.path.insert(0, LOCAL_DIR)
        import main; main.main()
    elif choice == '2':
        try:
            import urllib.request
            urllib.request.urlopen('http://127.0.0.1:5002/api/restart', timeout=3)
        except: pass
        time.sleep(3)
        sync_code()
        os.chdir(LOCAL_DIR); sys.path.insert(0, LOCAL_DIR)
        import main; main.main()
    elif choice == '3':
        try:
            import urllib.request
            urllib.request.urlopen('http://127.0.0.1:5002/api/restart', timeout=3)
        except: pass
        print('服务已停止'); time.sleep(1)
    elif choice == '4': sync_code(); input('按回车继续...')
    elif choice == '5': os.system('start http://127.0.0.1:5002')
    elif choice == '6': os.system('start http://127.0.0.1:5002/admin')
    elif choice == '0': return False
    return True

if __name__ == '__main__':
    os.makedirs(LOCAL_DIR, exist_ok=True)

    # PyInstaller bundle: 首次运行提取资源文件
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
        for d in ['tablet']:
            src = os.path.join(bundle_dir, d)
            dst = os.path.join(LOCAL_DIR, d)
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copytree(src, dst)
        for f in ['config.yaml']:
            src = os.path.join(bundle_dir, f)
            dst = os.path.join(LOCAL_DIR, f)
            if os.path.exists(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)

    # 每次启动从 Mac SMB 同步最新源码
    sync_code()

    os.chdir(LOCAL_DIR)
    sys.path.insert(0, LOCAL_DIR)

    # 尝试 GUI 模式
    _has_ctk = False
    try:
        import customtkinter
        _has_ctk = True
    except ImportError:
        pass

    if _has_ctk and os.path.exists(os.path.join(LOCAL_DIR, 'desktop_app.py')):
        print('[启动] 桌面 GUI 模式')
        from desktop_app import start_server, build_gui
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        time.sleep(3)
        build_gui().mainloop()
        sys.exit(0)

    # 没有 customtkinter → 尝试调系统 Python 自动构建 GUI EXE
    if os.path.exists(os.path.join(LOCAL_DIR, 'desktop_app.py')):
        print('[自升级] 正在自动构建 GUI 版 EXE（首次需要几分钟）...')
        try:
            import subprocess as _sp
            _sep = ';' if sys.platform == 'win32' else ':'
            _r = _sp.run([
                'python', '-m', 'PyInstaller',
                '--onefile', '--windowed', '--name', 'qiandao',
                '--add-data', f'tablet{_sep}tablet',
                '--add-data', f'config.yaml{_sep}.',
                '--hidden-import', 'customtkinter',
                '--hidden-import', 'win_card_listener',
                '--hidden-import', 'win_com_reader',
                '--hidden-import', 'win_window_reader',
                '--hidden-import', 'auth_manager',
                '--hidden-import', 'activate_tool',
                '--hidden-import', 'platform_utils',
                '--hidden-import', 'excel_manager',
                '--hidden-import', 'timer_manager',
                '--hidden-import', 'voice_broadcast',
                '--clean', 'desktop_app.py'
            ], cwd=LOCAL_DIR, capture_output=True, text=True, timeout=300)
            if _r.returncode == 0:
                _src = os.path.join(LOCAL_DIR, 'dist', 'qiandao.exe')
                _dst = os.path.join(os.environ.get('USERPROFILE', os.path.expanduser('~')), 'Desktop', 'qiandao.exe')
                if os.path.exists(_src):
                    shutil.copy2(_src, _dst)
                    print('[自升级] 完成！桌面上的 qiandao.exe 已升级为 GUI 版')
                    print('[自升级] 请关闭此窗口，双击桌面的 qiandao.exe')
                    time.sleep(10)
                    sys.exit(0)
            print(f'[自升级] 构建失败，可能需要先安装依赖')
            print(f'[自升级] 或双击 SMB 共享中的 build_exe.bat')
        except Exception as e:
            print(f'[自升级] 出错: {e}')

    # 回退：浏览器模式
    import main
    server_thread = threading.Thread(target=main.main, daemon=True)
    server_thread.start()
    time.sleep(3)
    import webbrowser
    webbrowser.open('http://127.0.0.1:5002/desktop')
    try:
        while server_thread.is_alive():
            server_thread.join(1)
    except KeyboardInterrupt:
        pass
