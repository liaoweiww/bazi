#!/usr/bin/env python3
"""
易经八字推算系统 - 主入口
支持 CLI 命令行模式和 API 服务模式

用法:
    # 初始化数据库
    python main.py init

    # 命令行排盘
    python main.py paipan --name 张三 --gender 男 --year 1990 --month 6 --day 15 --hour 8

    # 启动API服务
    python main.py serve [--port 5000]

    # 查看节气
    python main.py solar-terms --year 2024
"""
import sys
import os
import argparse
import json
from datetime import datetime

# 确保backend目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def cmd_init(args):
    """初始化数据库"""
    print("正在初始化数据库...")
    from data.database import init_db
    init_db()

    from data.seed_data import seed_all
    seed_all()
    print("数据库初始化完成！已创建所有基础数据表并填充古籍数据。")


def cmd_paipan(args):
    """命令行排盘"""
    from algorithm.paipan import paipan

    result = paipan(
        solar_year=args.year,
        solar_month=args.month,
        solar_day=args.day,
        hour=args.hour,
        minute=args.minute or 0,
        longitude=args.longitude or 120.0,
        latitude=args.latitude or 30.0,
        gender=args.gender or '男'
    )

    name = args.name or ''
    if name:
        result['name'] = name
        print(f"\n{'='*50}")
        print(f"  八字命盘：{name}")
        print(f"{'='*50}")
    else:
        print(f"\n{'='*50}")
        print(f"  八字排盘结果")
        print(f"{'='*50}")

    # 显示基本信息
    birth = result.get('birth_info', {})
    print(f"\n【出生信息】")
    print(f"  公历: {birth.get('solar_date', '')} {birth.get('solar_time', '')}")
    print(f"  农历: {birth.get('lunar_date', '')}")
    print(f"  真太阳时: {birth.get('true_solar_time', '')}")
    print(f"  性别: {birth.get('gender', '')}")

    # 显示四柱
    pillars = result.get('four_pillars', {})
    print(f"\n【四柱八字】")
    print(f"  {'柱位':<6} {'天干':<6} {'地支':<6} {'藏干':<20} {'纳音':<10} {'十神':<8}")
    print(f"  {'-'*56}")
    for pname, plabel in [('year', '年柱'), ('month', '月柱'), ('day', '日柱'), ('hour', '时柱')]:
        p = pillars.get(pname, {})
        canggan_str = '、'.join(p.get('canggan', []))
        print(f"  {plabel:<6} {p.get('gan', ''):<6} {p.get('zhi', ''):<6} {canggan_str:<20} {p.get('nayin', ''):<10} {p.get('shishen', ''):<8}")

    # 显示日主
    print(f"\n【日主】{result.get('day_master', '')} ({result.get('day_master_wuxing', '')})")

    # 显示五行
    wx = result.get('wuxing_count', {})
    print(f"\n【五行力量】")
    for w in ['金', '木', '水', '火', '土']:
        info = wx.get(w, {})
        if isinstance(info, dict):
            bar = '█' * int(info.get('score', 0))
            print(f"  {w}: {bar} (数量: {info.get('count', 0)}, 分值: {info.get('score', 0)})")

    # 显示身强身弱
    strength = result.get('strength', {})
    print(f"\n【身强身弱】{strength.get('level', '')} (评分: {strength.get('score', 0)})")
    print(f"  分析: {strength.get('details', '')}")

    # 显示格局
    geju = result.get('geju', {})
    print(f"\n【格局】{geju.get('type', '')} - {geju.get('name', '')}")
    print(f"  分析: {geju.get('analysis', '')}")

    # 显示喜用神
    yongji = result.get('yongji', {})
    print(f"\n【喜用神与忌神】")
    yong_shen = yongji.get('yong_shen', [])
    for ys in yong_shen:
        print(f"  用神: {ys.get('wuxing', '')} ({ys.get('shishen', '')}) - {ys.get('reason', '')}")
    ji_shen = yongji.get('ji_shen', [])
    for js in ji_shen:
        print(f"  忌神: {js.get('wuxing', '')} ({js.get('shishen', '')}) - {js.get('reason', '')}")
    if yongji.get('tiao_hou'):
        print(f"  调候: {yongji['tiao_hou']}")

    # 显示大运
    dayun = result.get('dayun', {})
    print(f"\n【大运】")
    print(f"  起运年龄: {dayun.get('start_age', 0)}岁")
    print(f"  排运方向: {dayun.get('direction', '')}")
    print(f"  {'运程':<12} {'干支':<8} {'纳音':<12}")
    print(f"  {'-'*32}")
    for dy in dayun.get('dayun_list', [])[:8]:
        print(f"  {dy.get('age_range', ''):<12} {dy.get('ganzhi', ''):<8} {dy.get('nayin', ''):<12}")

    # 显示当前流年
    liunian = dayun.get('liunian_current', {})
    if liunian:
        print(f"\n【{datetime.now().year}年流年】")
        print(f"  流年干支: {liunian.get('ganzhi', '')}")
        print(f"  五行: {liunian.get('wuxing', '')}")
        print(f"  分析: {liunian.get('analysis', '')}")

    print(f"\n{'='*50}\n")

    # 可选输出完整JSON
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_serve(args):
    """启动API服务"""
    from api.server import app
    port = args.port or 5000
    print("=" * 50)
    print("  易经八字推算系统 API Server")
    print(f"  地址: http://localhost:{port}")
    print(f"  健康检查: http://localhost:{port}/api/health")
    print("=" * 50)
    app.run(host='0.0.0.0', port=port, debug=not args.production)


def cmd_solar_terms(args):
    """查询节气"""
    from calendar.solar_terms import get_all_solar_terms
    year = args.year or datetime.now().year
    terms = get_all_solar_terms(year)
    print(f"\n{year}年 二十四节气:")
    print(f"  {'节气':<8} {'日期':<14} {'黄经':<6}")
    print(f"  {'-'*28}")
    for t in terms:
        print(f"  {t.get('name', ''):<8} {str(t.get('date', '')):<14} {t.get('longitude', '')}°")


def cmd_lunar(args):
    """公历转农历"""
    from calendar.lunar_solar import solar_to_lunar
    result = solar_to_lunar(args.year, args.month, args.day)
    print(f"\n公历 {args.year}-{args.month:02d}-{args.day:02d}")
    print(f"农历 {result.get('lunar_year', '')}年{result.get('lunar_month', '')}月{result.get('lunar_day', '')}")
    if result.get('leap_month'):
        print("  (闰月)")
    print(f"干支: {result.get('ganzhi_year', '')}年 {result.get('ganzhi_month', '')}月 {result.get('ganzhi_day', '')}日")
    print(f"生肖: {result.get('animal_year', '')}")


def main():
    parser = argparse.ArgumentParser(
        description='易经八字推算系统 - 专业古籍级命理排盘',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # init 子命令
    parser_init = subparsers.add_parser('init', help='初始化数据库')

    # paipan 子命令
    parser_paipan = subparsers.add_parser('paipan', help='八字排盘')
    parser_paipan.add_argument('--name', type=str, help='姓名')
    parser_paipan.add_argument('--gender', type=str, default='男', choices=['男', '女'], help='性别')
    parser_paipan.add_argument('--year', type=int, required=True, help='出生年(公历)')
    parser_paipan.add_argument('--month', type=int, required=True, help='出生月(公历)')
    parser_paipan.add_argument('--day', type=int, required=True, help='出生日(公历)')
    parser_paipan.add_argument('--hour', type=int, default=0, help='出生时(0-23,北京时间)')
    parser_paipan.add_argument('--minute', type=int, default=0, help='出生分')
    parser_paipan.add_argument('--longitude', type=float, help='出生地经度(东经为正)')
    parser_paipan.add_argument('--latitude', type=float, help='出生地纬度')
    parser_paipan.add_argument('--json', action='store_true', help='输出完整JSON')

    # serve 子命令
    parser_serve = subparsers.add_parser('serve', help='启动API服务')
    parser_serve.add_argument('--port', type=int, default=5000, help='服务端口(默认5000)')
    parser_serve.add_argument('--production', action='store_true', help='生产模式')

    # solar-terms 子命令
    parser_terms = subparsers.add_parser('solar-terms', help='查询节气')
    parser_terms.add_argument('--year', type=int, help='年份')

    # lunar 子命令
    parser_lunar = subparsers.add_parser('lunar', help='公历转农历')
    parser_lunar.add_argument('--year', type=int, required=True, help='公历年')
    parser_lunar.add_argument('--month', type=int, required=True, help='公历月')
    parser_lunar.add_argument('--day', type=int, required=True, help='公历日')

    args = parser.parse_args()

    if args.command == 'init':
        cmd_init(args)
    elif args.command == 'paipan':
        cmd_paipan(args)
    elif args.command == 'serve':
        cmd_serve(args)
    elif args.command == 'solar-terms':
        cmd_solar_terms(args)
    elif args.command == 'lunar':
        cmd_lunar(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
