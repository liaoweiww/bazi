#!/usr/bin/env python3
"""我的菜谱 - 后端服务入口"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def serve(port=5001):
    from api.server import app
    app.run(host='0.0.0.0', port=port, debug=True)


def init_db():
    from data.database import init_db
    init_db()


def seed():
    from data.database import init_db
    from data.seed_data import seed_all
    init_db()
    seed_all()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='我的菜谱 后端')
    sub = parser.add_subparsers(dest='cmd')

    p_serve = sub.add_parser('serve', help='启动API服务')
    p_serve.add_argument('--port', type=int, default=5001)

    sub.add_parser('init', help='初始化数据库')
    sub.add_parser('seed', help='初始化并填充种子数据')

    args = parser.parse_args()

    if args.cmd == 'serve':
        serve(port=args.port)
    elif args.cmd == 'init':
        init_db()
    elif args.cmd == 'seed':
        seed()
    else:
        parser.print_help()
