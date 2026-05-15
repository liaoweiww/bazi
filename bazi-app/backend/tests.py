#!/usr/bin/env python3
"""
易经八字APP - 系统集成测试
验证所有模块的正确性
"""
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_database():
    """测试数据库基础数据"""
    print("=" * 60)
    print("测试1: 数据库基础数据")
    print("=" * 60)

    from data.queries import (
        get_all_tiangan, get_all_dizhi, get_all_jiazi,
        get_shishen, get_wuxing_relation, get_canggan,
        is_database_ready
    )

    assert is_database_ready(), "数据库未就绪"

    tiangan = get_all_tiangan()
    assert len(tiangan) == 10, f"天干数量错误: {len(tiangan)}"
    assert tiangan[0]['name'] == '甲', f"第一天干应为甲: {tiangan[0]['name']}"
    print(f"  ✓ 天干: 10条数据正确")

    dizhi = get_all_dizhi()
    assert len(dizhi) == 12, f"地支数量错误: {len(dizhi)}"
    assert dizhi[0]['name'] == '子', f"第一地支应为子: {dizhi[0]['name']}"
    # 验证藏干
    zi_canggan = get_canggan('子')
    assert '癸' in zi_canggan, f"子藏干应含癸: {zi_canggan}"
    yin_canggan = get_canggan('寅')
    assert '甲' in yin_canggan, f"寅藏干应含甲: {yin_canggan}"
    print(f"  ✓ 地支: 12条数据正确, 藏干验证通过")

    jiazi = get_all_jiazi()
    assert len(jiazi) == 60, f"六十甲子数量错误: {len(jiazi)}"
    assert jiazi[0]['ganzhi'] == '甲子', f"第一甲子应为甲子: {jiazi[0]['ganzhi']}"
    assert jiazi[0]['nayin'] == '海中金', f"甲子纳音应为海中金: {jiazi[0]['nayin']}"
    assert jiazi[59]['ganzhi'] == '癸亥', f"第60甲子应为癸亥: {jiazi[59]['ganzhi']}"
    assert jiazi[59]['nayin'] == '大海水', f"癸亥纳音应为大海水: {jiazi[59]['nayin']}"
    print(f"  ✓ 六十甲子: 60条数据正确, 纳音验证通过")

    # 十神验证
    assert get_shishen('甲', '丙')['shishen'] == '食神', "甲见丙应为食神"
    assert get_shishen('甲', '庚')['shishen'] == '七杀', "甲见庚应为七杀"
    assert get_shishen('甲', '己')['shishen'] == '正财', "甲见己应为正财"
    assert get_shishen('甲', '癸')['shishen'] == '正印', "甲见癸应为正印"
    print(f"  ✓ 十神映射: 逻辑正确")

    # 五行生克验证
    assert get_wuxing_relation('木', '火')['relation'] == '生', "木应生火"
    assert get_wuxing_relation('木', '土')['relation'] == '克', "木应克土"
    assert get_wuxing_relation('金', '木')['relation'] == '克', "金应克木"
    assert get_wuxing_relation('水', '木')['relation'] == '生', "水应生木"
    print(f"  ✓ 五行生克: 规则正确")

    print(f"\n  数据库基础数据全部通过！\n")


def test_calendar():
    """测试历法模块"""
    print("=" * 60)
    print("测试2: 历法模块")
    print("=" * 60)

    try:
        from calendar.solar_terms import get_all_solar_terms
        terms = get_all_solar_terms(2024)
        assert len(terms) == 24, f"节气数量应为24: {len(terms)}"
        # 节气可能从冬至或立春开始，检查是否包含关键节气
        term_names = [t['name'] for t in terms]
        assert '立春' in term_names, "应包含立春"
        assert '冬至' in term_names, "应包含冬至"
        assert '夏至' in term_names, "应包含夏至"
        assert '秋分' in term_names, "应包含秋分"
        print(f"  ✓ 节气查询: 2024年24节气完整")

        from calendar.lunar_solar import solar_to_lunar
        lunar = solar_to_lunar(2024, 2, 10)
        assert 'lunar_year' in lunar, "农历转换应返回lunar_year"
        print(f"  ✓ 公历转农历: 功能正常")

        from calendar.true_solar import get_true_solar_time
        true_time = get_true_solar_time(
            datetime(2024, 6, 15, 8, 0),
            longitude=116.4,
            latitude=39.9
        )
        assert isinstance(true_time, datetime), "真太阳时应返回datetime对象"
        print(f"  ✓ 真太阳时矫正: 功能正常")

        from calendar.month_pillar import get_month_pillar, get_hour_pillar
        mp = get_month_pillar(2024, datetime(2024, 2, 5))
        assert len(mp) == 2, "月柱应返回(天干, 地支)"
        hp = get_hour_pillar('甲', 8)
        assert len(hp) == 2, "时柱应返回(天干, 地支)"
        print(f"  ✓ 月柱/时柱计算: 功能正常")

        print(f"\n  历法模块全部通过！\n")
    except ImportError as e:
        print(f"  ⚠ 历法模块尚未就绪: {e}\n")
    except Exception as e:
        print(f"  ✗ 历法模块测试失败: {e}\n")


def test_paipan():
    """测试核心排盘算法"""
    print("=" * 60)
    print("测试3: 核心排盘算法")
    print("=" * 60)

    try:
        from algorithm.paipan import paipan

        # 测试案例: 1990年6月15日 8:30 男
        result = paipan(
            solar_year=1990,
            solar_month=6,
            solar_day=15,
            hour=8,
            minute=30,
            longitude=116.4,
            latitude=39.9,
            gender='男'
        )

        assert 'four_pillars' in result, "排盘结果应包含four_pillars"
        pillars = result['four_pillars']

        for pname in ['year', 'month', 'day', 'hour']:
            assert pname in pillars, f"四柱应包含{pname}"
            p = pillars[pname]
            assert 'gan' in p, f"{pname}柱应有天干"
            assert 'zhi' in p, f"{pname}柱应有地支"
            assert 'ganzhi' in p, f"{pname}柱应有干支组合"

        print(f"  ✓ 四柱: {pillars['year']['ganzhi']} {pillars['month']['ganzhi']} {pillars['day']['ganzhi']} {pillars['hour']['ganzhi']}")

        assert 'day_master' in result, "应有日主"
        assert 'day_master_wuxing' in result, "应有日主五行"
        print(f"  ✓ 日主: {result['day_master']}({result['day_master_wuxing']})")

        assert 'wuxing_count' in result, "应有五行统计"
        assert 'strength' in result, "应有身强身弱判定"
        print(f"  ✓ 身强身弱: {result['strength'].get('level', '')}")

        assert 'geju' in result, "应有格局判定"
        print(f"  ✓ 格局: {result['geju'].get('name', '')}")

        assert 'yongji' in result, "应有喜用神"
        print(f"  ✓ 喜用神: {result['yongji'].get('yong_shen', [])}")

        assert 'dayun' in result, "应有大运"
        print(f"  ✓ 大运: 起运{result['dayun'].get('start_age', '')}岁")

        assert 'birth_info' in result, "应有出生信息"
        print(f"  ✓ 出生信息: {result['birth_info'].get('solar_date', '')}")

        print(f"\n  核心排盘算法全部通过！\n")
        return result
    except ImportError as e:
        print(f"  ⚠ 算法模块尚未就绪: {e}\n")
        return None
    except Exception as e:
        import traceback
        print(f"  ✗ 排盘测试失败: {e}")
        traceback.print_exc()
        print()
        return None


def test_texts():
    """测试文案引擎"""
    print("=" * 60)
    print("测试4: 古籍文案引擎")
    print("=" * 60)

    try:
        from texts.engine import TextEngine
        engine = TextEngine()

        # 创建模拟排盘结果
        mock_result = {
            'day_master': '甲',
            'day_master_wuxing': '木',
            'four_pillars': {
                'year': {'gan': '庚', 'zhi': '午', 'ganzhi': '庚午', 'nayin': '路旁土', 'shishen': '七杀', 'canggan': ['丁', '己']},
                'month': {'gan': '壬', 'zhi': '午', 'ganzhi': '壬午', 'nayin': '杨柳木', 'shishen': '偏印', 'canggan': ['丁', '己']},
                'day': {'gan': '甲', 'zhi': '寅', 'ganzhi': '甲寅', 'nayin': '大溪水', 'shishen': '比肩', 'canggan': ['甲', '丙', '戊']},
                'hour': {'gan': '戊', 'zhi': '辰', 'ganzhi': '戊辰', 'nayin': '大林木', 'shishen': '偏财', 'canggan': ['戊', '乙', '癸']}
            },
            'wuxing_count': {'金': {'count': 1, 'score': 1}, '木': {'count': 3, 'score': 4}, '水': {'count': 1, 'score': 1.5}, '火': {'count': 2, 'score': 2}, '土': {'count': 3, 'score': 3.5}},
            'strength': {'level': '身强', 'score': 75, 'details': '甲木得寅木强根，月干壬水相生'},
            'geju': {'type': '正格', 'name': '建禄格', 'analysis': '甲生寅月，建禄格'},
            'yongji': {'yong_shen': [{'wuxing': '火', 'shishen': '食神'}], 'ji_shen': [{'wuxing': '水', 'shishen': '正印'}], 'xian_shen': [], 'tiao_hou': ''},
            'dayun': {'start_age': 6, 'direction': '顺排', 'dayun_list': [{'age_range': '6-15', 'ganzhi': '癸未'}], 'current_dayun': {}, 'liunian_current': {}}
        }

        interpretation = engine.interpret(mock_result)

        assert 'four_pillars_interpret' in interpretation
        assert 'wuxing_interpret' in interpretation
        assert 'shishen_interpret' in interpretation
        assert 'geju_interpret' in interpretation
        assert 'overall' in interpretation

        print(f"  ✓ 四柱解读: {len(interpretation['four_pillars_interpret'])}柱")
        print(f"  ✓ 五行解读: 身{interpretation['wuxing_interpret'].get('strength_level', '')}")
        print(f"  ✓ 格局解读: {interpretation['geju_interpret'].get('name', '')}")
        print(f"  ✓ 总览: {interpretation['overall'][:50]}...")

        print(f"\n  古籍文案引擎全部通过！\n")
    except ImportError as e:
        print(f"  ⚠ 文案模块尚未就绪: {e}\n")
    except Exception as e:
        print(f"  ✗ 文案测试失败: {e}\n")


def main():
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + "  易经八字推算系统 - 集成测试".center(52) + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    test_database()
    test_calendar()
    paipan_result = test_paipan()
    test_texts()

    print("=" * 60)
    print("  集成测试完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
