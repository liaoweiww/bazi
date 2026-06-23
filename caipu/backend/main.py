"""家庭私厨 — 命令行入口

用法：
  python main.py init              # 初始化数据库表
  python main.py seed              # 灌入系统食材数据
  python main.py serve [--port]    # 启动 API 服务器
"""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def cmd_init(_args):
    """建表"""
    from data.database import init_db
    init_db()
    print("✅ 数据库表已创建 (caipu_app)")


def cmd_seed(_args):
    """灌入 192 条系统食材"""
    from data.seed_data import seed_ingredients
    count = seed_ingredients()
    print(f"✅ 已灌入 {count} 条系统食材")


def cmd_serve(args):
    """启动 Flask 服务器"""
    from api.server import app
    from config import DEFAULT_PORT
    port = args.port or DEFAULT_PORT
    print(f"🍳 家庭私厨 API 启动 → http://0.0.0.0:{port}")
    print(f"   健康检查: http://127.0.0.1:{port}/api/health")
    app.run(host='0.0.0.0', port=port, debug=not args.production)


def main():
    parser = argparse.ArgumentParser(description='家庭私厨后端')
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('init', help='初始化数据库表')
    sub.add_parser('seed', help='灌入系统食材数据')

    serve_p = sub.add_parser('serve', help='启动 API 服务器')
    serve_p.add_argument('--port', type=int, default=None, help='监听端口 (默认: 5000)')
    serve_p.add_argument('--production', action='store_true', help='生产模式（关闭 debug）')

    args = parser.parse_args()

    if args.command == 'init':
        cmd_init(args)
    elif args.command == 'seed':
        cmd_seed(args)
    elif args.command == 'serve':
        cmd_serve(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
