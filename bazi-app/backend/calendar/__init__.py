"""
日历模块 - Calendar Layer for Bazi App

提供八字排盘所需的核心历法计算能力。

子模块:
  - solar_terms    : 24节气精确计算（寿星万年历VSOP87简化算法）
  - lunar_solar    : 公历农历双向转换（1900-2100年查表法）
  - true_solar     : 真太阳时矫正（经度修正 + 均时差）
  - month_pillar   : 月柱/时柱干支计算（五虎遁/五鼠遁）

所有算法自包含，仅依赖Python标准库（math, datetime）。
"""

# ---- solar_terms 模块 ----
from .solar_terms import (
    # 常量
    SOLAR_TERM_NAMES,
    SOLAR_TERM_LONGITUDE,
    MONTH_BRANCH_NAMES,
    TERM_NAME_TO_LONGITUDE,
    LONGITUDE_TO_TERM,
    SOLAR_TERM_APPROX_RANGE,
    MONTH_PILLAR_TERMS,

    # 核心函数
    get_solar_term,
    get_all_solar_terms,
    get_current_solar_term,
    get_month_branch_by_solar_term,
    verify_solar_term_date,
)

# ---- lunar_solar 模块 ----
from .lunar_solar import (
    solar_to_lunar,
    lunar_to_solar,
    get_lunar_month_days,
    get_lunar_year_info,
    get_lunar_new_year,
    is_lunar_leap_year,
    get_ganzhi_day,
    get_ganzhi_year,
)

# ---- true_solar 模块 ----
from .true_solar import (
    get_true_solar_time,
    get_true_solar_time_detailed,
    get_equation_of_time,
    get_eot,
    get_time_zone_offset,
    get_time_zone_from_longitude,
)

# ---- month_pillar 模块 ----
from .month_pillar import (
    TIANGAN,
    DIZHI,
    get_month_pillar,
    get_hour_pillar,
    get_month_branch_by_date,
    get_day_gan_by_hour_gan,
    get_hour_branch_by_time,
    get_hour_branch,
)


__all__ = [
    # solar_terms
    "SOLAR_TERM_NAMES",
    "SOLAR_TERM_LONGITUDE",
    "MONTH_BRANCH_NAMES",
    "TERM_NAME_TO_LONGITUDE",
    "LONGITUDE_TO_TERM",
    "SOLAR_TERM_APPROX_RANGE",
    "MONTH_PILLAR_TERMS",
    "get_solar_term",
    "get_all_solar_terms",
    "get_current_solar_term",
    "get_month_branch_by_solar_term",
    "verify_solar_term_date",

    # lunar_solar
    "solar_to_lunar",
    "lunar_to_solar",
    "get_lunar_month_days",
    "get_lunar_year_info",
    "get_lunar_new_year",
    "is_lunar_leap_year",
    "get_ganzhi_day",
    "get_ganzhi_year",

    # true_solar
    "get_true_solar_time",
    "get_true_solar_time_detailed",
    "get_equation_of_time",
    "get_eot",
    "get_time_zone_offset",
    "get_time_zone_from_longitude",

    # month_pillar
    "TIANGAN",
    "DIZHI",
    "get_month_pillar",
    "get_hour_pillar",
    "get_month_branch_by_date",
    "get_day_gan_by_hour_gan",
    "get_hour_branch_by_time",
    "get_hour_branch",
]
