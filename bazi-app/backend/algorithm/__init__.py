"""
核心算法模块 - Algorithm Layer
==============================
提供八字排盘、五行量化、格局判定、喜用神、大运流年等完整功能。

所有算法手写实现，仅依赖 Python 标准库和项目内的 _constants 数据模块。

模块结构:
    _constants.py   - 基础常量 (天干、地支、藏干、纳音、节气、五行生克等)
    paipan.py       - 四柱排盘主算法 (真太阳时、节气计算、五虎遁、五鼠遁)
    wuxing_calc.py  - 五行量化与身强身弱判定
    geju.py         - 格局判定 (正格、变格、专旺格)
    yongji.py       - 喜用神与忌神
    dayun.py        - 大运与流年推算
    shishen_calc.py - 十神计算
"""

# 排盘主函数
from .paipan import (
    paipan,
    get_solar_terms_for_year,
    get_lichun_date,
)

# 五行量化与身强身弱
from .wuxing_calc import (
    count_wuxing,
    check_deling,
    check_dedi,
    check_deshi,
    determine_strength,
)

# 格局判定
from .geju import (
    determine_geju,
)

# 喜用神
from .yongji import (
    determine_yongji,
)

# 大运流年
from .dayun import (
    calculate_dayun,
    calculate_liunian,
    get_current_dayun,
    get_liunian_multi_year,
)

# 十神
from .shishen_calc import (
    calculate_shishen,
    get_all_shishen_mapping,
    get_shishen_wuxing,
    analyze_shishen_distribution,
    classify_shishen_groups,
)

# 常量 (便捷访问)
from ._constants import (
    GAN, GAN_WUXING, GAN_YINYANG, GAN_WUXING_LIST, GAN_YINYANG_LIST,
    ZHI, ZHI_WUXING, ZHI_YINYANG, ZHI_WUXING_LIST, ZHI_YINYANG_LIST,
    CANG_GAN, NAYIN_DATA,
    WUXING_SHENG, WUXING_KE,
    SHICHEN_MAP,
)

__all__ = [
    # 排盘
    "paipan",
    "get_solar_terms_for_year",
    "get_lichun_date",
    # 五行量化
    "count_wuxing",
    "check_deling",
    "check_dedi",
    "check_deshi",
    "determine_strength",
    # 格局
    "determine_geju",
    # 喜用神
    "determine_yongji",
    # 大运流年
    "calculate_dayun",
    "calculate_liunian",
    "get_current_dayun",
    "get_liunian_multi_year",
    # 十神
    "calculate_shishen",
    "get_all_shishen_mapping",
    "get_shishen_wuxing",
    "analyze_shishen_distribution",
    "classify_shishen_groups",
    # 常量
    "GAN", "GAN_WUXING", "GAN_YINYANG", "GAN_WUXING_LIST", "GAN_YINYANG_LIST",
    "ZHI", "ZHI_WUXING", "ZHI_YINYANG", "ZHI_WUXING_LIST", "ZHI_YINYANG_LIST",
    "CANG_GAN", "NAYIN_DATA",
    "WUXING_SHENG", "WUXING_KE",
    "SHICHEN_MAP",
]
