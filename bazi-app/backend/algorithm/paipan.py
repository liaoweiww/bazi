"""
四柱排盘主算法
==============
八字排盘的核心模块。根据出生年月日时和经纬度，
计算四柱（年柱、月柱、日柱、时柱）天干地支。
包含真太阳时矫正、节气计算、五虎遁、五鼠遁等核心算法。

所有算法独立手写实现，不依赖第三方命理库，仅使用Python标准库。
"""

import math
from datetime import datetime, date, timedelta
from typing import Dict, Tuple, Optional, List

from ._constants import (
    GAN, GAN_WUXING_LIST, GAN_YINYANG_LIST,
    ZHI, ZHI_WUXING_LIST, ZHI_YINYANG_LIST,
    CANG_GAN, NAYIN_DATA,
    SOLAR_TERM_C, SOLAR_TERM_NAMES, SOLAR_TERM_MONTH,
    JIE_INDICES, JIE_ZHI, JIE_MONTH_NUM,
    CENTURY21_CORRECTION,
    SHICHEN_MAP,
    BASE_YEAR, BASE_MONTH, BASE_DAY,
    BASE_DAY_GAN_INDEX, BASE_DAY_ZHI_INDEX,
    LUNAR_NUMBERS, LUNAR_DAY_NUMBERS,
)


# =============================================================================
# 工具函数
# =============================================================================

def _gan_index(gan: str) -> int:
    """天干名称 -> 索引"""
    return GAN.index(gan)


def _zhi_index(zhi: str) -> int:
    """地支名称 -> 索引"""
    return ZHI.index(zhi)


def _is_leap_year(year: int) -> bool:
    """判断公历闰年"""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def _days_in_month(year: int, month: int) -> int:
    """某年某月的天数"""
    if month == 2:
        return 29 if _is_leap_year(year) else 28
    if month in (4, 6, 9, 11):
        return 30
    return 31


def _day_of_year(year: int, month: int, day: int) -> int:
    """返回某日期在该年中的第几天 (1-based)"""
    days_before = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    doy = days_before[month - 1] + day
    if month > 2 and _is_leap_year(year):
        doy += 1
    return doy


def _date_from_day_of_year(year: int, doy: int) -> Tuple[int, int]:
    """从年积日反推月日"""
    if _is_leap_year(year):
        dims = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        dims = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    month = 1
    for dim in dims:
        if doy <= dim:
            return month, doy
        doy -= dim
        month += 1
    return 12, doy


# =============================================================================
# 儒略日计算
# =============================================================================

def _julian_day(year: int, month: int, day: int,
                hour: float = 0.0) -> float:
    """
    公历日期转儒略日数 (Julian Day Number)。

    使用 Meeus「天文算法」中的公式。
    """
    if month <= 2:
        year -= 1
        month += 12
    A = year // 100
    B = 2 - A + A // 4
    jd = int(365.25 * (year + 4716)) + \
         int(30.6001 * (month + 1)) + \
         day + B - 1524.5
    jd += hour / 24.0
    return jd


def _jd_to_calendar(jd: float) -> Tuple[int, int, int, float]:
    """
    儒略日转公历日期。

    返回:
        (年, 月, 日, 小时_小数)
    """
    jd += 0.5
    Z = int(jd)
    F = jd - Z
    if Z < 2299161:
        A = Z
    else:
        alpha = int((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - int(alpha / 4)
    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)
    day_val = B - D - int(30.6001 * E) + F
    day_int = int(day_val)
    day_frac = day_val - day_int
    if E < 14:
        month = E - 1
    else:
        month = E - 13
    if month > 2:
        year = C - 4716
    else:
        year = C - 4715
    hour_frac = day_frac * 24.0
    return year, month, day_int, hour_frac


# =============================================================================
# 太阳视黄经 (用于精确节气计算)
# =============================================================================

def _sun_longitude(jd: float) -> float:
    """
    计算给定儒略日时的太阳视黄经。

    使用 Meeus 天文算法低精度公式，精度约 0.01°。

    返回:
        太阳视黄经，度数 [0, 360)
    """
    T = (jd - 2451545.0) / 36525.0

    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
    M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
    M_rad = math.radians(M % 360)

    C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M_rad) \
        + (0.019993 - 0.000101 * T) * math.sin(2.0 * M_rad) \
        + 0.000289 * math.sin(3.0 * M_rad)

    return (L0 + C) % 360.0


# 24节气近似日期 (月, 日) - 用于牛顿迭代初值
_SOLAR_TERM_APPROX = [
    (1, 6),  (1, 20),    #  0:小寒,  1:大寒
    (2, 4),  (2, 19),    #  2:立春,  3:雨水
    (3, 6),  (3, 21),    #  4:惊蛰,  5:春分
    (4, 5),  (4, 20),    #  6:清明,  7:谷雨
    (5, 6),  (5, 21),    #  8:立夏,  9:小满
    (6, 6),  (6, 22),    # 10:芒种, 11:夏至
    (7, 7),  (7, 23),    # 12:小暑, 13:大暑
    (8, 8),  (8, 23),    # 14:立秋, 15:处暑
    (9, 8),  (9, 23),    # 16:白露, 17:秋分
    (10, 8), (10, 24),   # 18:寒露, 19:霜降
    (11, 7), (11, 22),   # 20:立冬, 21:小雪
    (12, 7), (12, 22),   # 22:大雪, 23:冬至
]


def _find_solar_term_jd(year: int, term_index: int) -> float:
    """
    使用牛顿迭代法查找指定节气的精确儒略日。

    参数:
        year: 目标年份
        term_index: 节气索引 0=小寒, ..., 23=冬至

    返回:
        该节气的儒略日
    """
    # 目标黄经角度: 小寒=285°, 依次+15°
    angle_deg = (term_index * 15 + 285) % 360

    # 使用近似日期作为初始猜测 (同一年内)
    approx_month, approx_day = _SOLAR_TERM_APPROX[term_index]
    jd = _julian_day(year, approx_month, approx_day, 12.0)

    # 牛顿迭代：每次按太阳经度差修正 JD
    for _ in range(10):
        lon = _sun_longitude(jd)
        diff = (angle_deg - lon) % 360.0
        if diff > 180.0:
            diff -= 360.0
        if abs(diff) < 0.0005:  # 约 2 角秒精度
            break
        jd += diff  # 近似: 1° ≈ 1 天

    return jd


def _get_solar_term_exact(year: int, term_index: int) -> Tuple[int, int, int, float]:
    """
    使用天文算法精确计算指定年份的24节气日期。

    参数:
        year: 年份
        term_index: 0=小寒, 1=大寒, ..., 23=冬至

    返回:
        (年, 月, 日, 小时小数)

    注：term_index 0 (小寒) 在1月，term_index 23 (冬至) 在12月，
    所有节气均在同一日历年内。
    """
    jd = _find_solar_term_jd(year, term_index)
    y, m, d, h = _jd_to_calendar(jd)

    # 校验：节气应落在预期月份附近
    expected_month = _SOLAR_TERM_APPROX[term_index][0]
    if m != expected_month:
        # 可能收敛到相邻年份的解，用预期月份附近的年份重新计算
        if m < expected_month:
            # 收敛到了下一年
            jd = _find_solar_term_jd(year - 1, term_index)
        else:
            # 收敛到了上一年
            jd = _find_solar_term_jd(year + 1, term_index)
        y, m, d, h = _jd_to_calendar(jd)

    return y, m, d, h


def _get_solar_term_date(year: int, term_index: int) -> Tuple[int, int, int]:
    """
    获取指定年份的24节气日期。

    优先使用精确天文算法，异常时回退到 C 值公式。

    返回:
        (年, 月, 日)
    """
    try:
        y, m, d, _ = _get_solar_term_exact(year, term_index)
        return y, m, d
    except Exception:
        return _get_solar_term_fallback(year, term_index)


def _get_solar_term_fallback(year: int, term_index: int) -> Tuple[int, int, int]:
    """
    使用 C 值公式计算节气日期 (回退方案)。
    公式: day ≈ int(C + 0.2422*(year-1900) - floor((year-1900)/4))
    """
    c = SOLAR_TERM_C[term_index]
    month = SOLAR_TERM_MONTH[term_index]
    offset = 0.2422 * (year - 1900) - ((year - 1900) // 4)
    day_approx = c + offset

    if year >= 2000 and term_index in CENTURY21_CORRECTION:
        day_approx += 1.0
    day = int(day_approx)

    if term_index <= 1:
        result_year = year
        result_month = 1
        if day < 1:
            day += 31
            result_month = 12
            result_year = year - 1
        elif day > 31:
            day -= 31
            result_month = 2
        return result_year, result_month, day

    max_day = _days_in_month(year, month)
    if day > max_day:
        day -= max_day
        month += 1
        if month > 12:
            month = 1
            year += 1
    elif day < 1:
        month -= 1
        if month < 1:
            month = 12
            year -= 1
        day += _days_in_month(year, month)
    return year, month, day


# =============================================================================
# 真太阳时矫正
# =============================================================================

def _calc_true_solar_time(year: int, month: int, day: int,
                          hour: int, minute: int,
                          longitude: float) -> Tuple[int, int, float]:
    """
    计算真太阳时。

    真太阳时 = 平太阳时 + 均时差(EoT) + 经度修正

    返回:
        (日期偏移天数, 真太阳时_整数, 真太阳分_小数)
    """
    # 经度修正: 北京时间基于120°E, 每度差4分钟
    lon_correction = (longitude - 120.0) * 4.0

    # 均时差 (Equation of Time)
    doy = _day_of_year(year, month, day)
    B = math.radians(360.0 / 365.0 * (doy - 81))
    eot = 9.87 * math.sin(2.0 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)

    total_offset = lon_correction + eot  # 分钟
    total_minutes = hour * 60.0 + minute + total_offset
    true_hour_float = total_minutes / 60.0

    day_offset = 0
    while true_hour_float >= 24.0:
        true_hour_float -= 24.0
        day_offset += 1
    while true_hour_float < 0.0:
        true_hour_float += 24.0
        day_offset -= 1

    true_hour_int = int(true_hour_float)
    true_minute_frac = (true_hour_float - true_hour_int) * 60.0
    return day_offset, true_hour_int, true_minute_frac


# =============================================================================
# 子时日期调整 (23:00后日柱算次日)
# =============================================================================

def _adjust_for_zishi(year: int, month: int, day: int,
                      hour_float: float) -> Tuple[int, int, int]:
    """子时(23:00)后日柱算次日"""
    if hour_float >= 23.0:
        d = date(year, month, day) + timedelta(days=1)
        return d.year, d.month, d.day
    return year, month, day


# =============================================================================
# 年柱计算 (以立春为界)
# =============================================================================

def _calc_year_pillar(solar_year: int, solar_month: int, solar_day: int
                      ) -> Tuple[int, str, str]:
    """
    计算年柱。

    规则: 以立春为年柱分界点 (NOT 农历正月初一!)
    年干 = (八字年 - 4) % 10
    年支 = (八字年 - 4) % 12

    返回:
        (八字年, 年干, 年支)
    """
    lichun_y, lichun_m, lichun_d = _get_solar_term_date(solar_year, 2)

    if (solar_month < lichun_m) or (solar_month == lichun_m and solar_day < lichun_d):
        bazi_year = solar_year - 1
    else:
        bazi_year = solar_year

    year_gan = GAN[(bazi_year - 4) % 10]
    year_zhi = ZHI[(bazi_year - 4) % 12]
    return bazi_year, year_gan, year_zhi


# =============================================================================
# 月柱计算 (年上起月法 / 五虎遁)
# =============================================================================

def _get_month_index(solar_year: int, solar_month: int, solar_day: int) -> int:
    """
    根据出生日期确定八字月份序号 (0=寅月, ..., 11=丑月)。

    通过比较出生日期与12个"节"的日期来确定月份区间。
    """
    # 构建出生日期在 year-1, year, year+1 范围的节气序列
    # 关键节气: 大雪(year-1), 小寒(year), 立春(year), ..., 大雪(year), 小寒(year+1)

    # 收集相关节的日期 (month_idx 0=寅, ..., 11=丑)
    jie_list = []
    for month_idx in range(12):
        term_idx = JIE_INDICES[month_idx]
        if month_idx >= 10:  # 大雪(10), 小寒(11) - 可能需要跨年
            y_prev, m_prev, d_prev = _get_solar_term_date(solar_year - 1, term_idx)
            jie_list.append((month_idx, y_prev, m_prev, d_prev, f"{solar_year - 1}"))
        y_cur, m_cur, d_cur = _get_solar_term_date(solar_year, term_idx)
        jie_list.append((month_idx, y_cur, m_cur, d_cur, f"{solar_year}"))
        if month_idx <= 1:  # 寅月(0), 卯月(1) - 可能在下一年
            y_next, m_next, d_next = _get_solar_term_date(solar_year + 1, term_idx)
            jie_list.append((month_idx, y_next, m_next, d_next, f"{solar_year + 1}"))

    # 按日期排序
    jie_list.sort(key=lambda x: (x[1], x[2], x[3]))

    # 出生日期
    birth = (solar_year, solar_month, solar_day)

    # 找到第一个大于出生日期的节，前一个节就是当前月份
    for i in range(len(jie_list)):
        jie_ymd = (jie_list[i][1], jie_list[i][2], jie_list[i][3])
        if birth < jie_ymd:
            if i == 0:
                return jie_list[-1][0]  # 在最早节气之前
            return jie_list[i - 1][0]

    return jie_list[-1][0]


def _calc_month_pillar(year: int, month: int, day: int,
                       year_gan: str) -> Tuple[int, str, str]:
    """
    计算月柱 (年上起月法/五虎遁)。

    返回:
        (月份序号, 月干, 月支)
    """
    month_idx = _get_month_index(year, month, day)
    month_zhi = JIE_ZHI[month_idx]

    # 五虎遁口诀:
    # 甲己之年丙作首 → gan%5==0 → 寅月起丙(idx 2)
    # 乙庚之岁戊为头 → gan%5==1 → 寅月起戊(idx 4)
    # 丙辛必定寻庚起 → gan%5==2 → 寅月起庚(idx 6)
    # 丁壬壬位顺行流 → gan%5==3 → 寅月起壬(idx 8)
    # 戊癸何方发甲寅 → gan%5==4 → 寅月起甲(idx 0)
    yg_idx = _gan_index(year_gan)
    base = (yg_idx % 5) * 2 + 2  # 寅月起的天干索引
    month_gan = GAN[(base + month_idx) % 10]

    return month_idx, month_gan, month_zhi


# =============================================================================
# 日柱计算
# =============================================================================

def _calc_day_pillar(year: int, month: int, day: int) -> Tuple[str, str]:
    """
    计算日柱天干地支。

    以 1900-01-01 (甲戌日) 为基准计算天数差。
    每 60 天一个甲子循环。

    返回:
        (日干, 日支)
    """
    base_date = date(BASE_YEAR, BASE_MONTH, BASE_DAY)
    target_date = date(year, month, day)
    offset = (target_date - base_date).days

    gan_idx = (BASE_DAY_GAN_INDEX + offset) % 10
    zhi_idx = (BASE_DAY_ZHI_INDEX + offset) % 12

    return GAN[gan_idx], ZHI[zhi_idx]


# =============================================================================
# 时柱计算 (日上起时法 / 五鼠遁)
# =============================================================================

def _get_shichen(hour_float: float) -> Tuple[int, str]:
    """
    根据真太阳时确定时辰。

    返回:
        (地支索引, 时辰名)
    """
    h = hour_float % 24.0
    if h >= 23.0 or h < 1.0:
        return 0, "子"
    for start_h, end_h, name in SHICHEN_MAP:
        if start_h <= h < end_h:
            return ZHI.index(name), name
    return 0, "子"


def _calc_hour_pillar(true_hour_float: float, day_gan: str
                      ) -> Tuple[str, str, str]:
    """
    计算时柱 (日上起时法/五鼠遁)。

    口诀:
    甲己还加甲 → gan%5==0 → 子时起甲(idx 0)
    乙庚丙作初 → gan%5==1 → 子时起丙(idx 2)
    丙辛从戊起 → gan%5==2 → 子时起戊(idx 4)
    丁壬庚子居 → gan%5==3 → 子时起庚(idx 6)
    戊癸何方发 → gan%5==4 → 子时起壬(idx 8)

    返回:
        (时干, 时支, 时辰名)
    """
    zhi_idx, shichen = _get_shichen(true_hour_float)
    hour_zhi = ZHI[zhi_idx]

    dg_idx = _gan_index(day_gan)
    base = (dg_idx % 5) * 2
    hour_gan = GAN[(base + zhi_idx) % 10]

    return hour_gan, hour_zhi, shichen


# =============================================================================
# 纳音和藏干
# =============================================================================

def _get_nayin(gan: str, zhi: str) -> Tuple[str, str]:
    """
    获取某干支组合的纳音。

    返回:
        (纳音名称, 纳音五行)
    """
    g_idx = _gan_index(gan)
    z_idx = _zhi_index(zhi)

    # 在 60 甲子中的序号
    k = (5 * (z_idx - g_idx) // 2) % 6
    n = (g_idx + 10 * k) % 60
    return NAYIN_DATA[n // 2]


def _get_canggan(zhi: str) -> list:
    """获取某地支的藏干列表"""
    cg_list = CANG_GAN.get(zhi, [])
    return [item[0] for item in cg_list]


# =============================================================================
# 简化农历推算
# =============================================================================

def _solar_to_lunar_approx(year: int, month: int, day: int,
                            bazi_year: int) -> str:
    """
    简化农历推算 (近似)。

    使用节气确定月份，用月相估算农历日。
    """
    lunar_year_gan = GAN[(bazi_year - 4) % 10]
    lunar_year_zhi = ZHI[(bazi_year - 4) % 12]

    month_idx = _get_month_index(year, month, day)
    lunar_month_num = month_idx + 1  # 寅月→正月

    # 使用儒略日计算月相
    jd = _julian_day(year, month, day, 12.0)
    ref_new_moon_jd = 2451549.05  # 2000-01-06 近似新月
    synodic_month = 29.530588
    days_since_ref = jd - ref_new_moon_jd
    lunar_day_float = days_since_ref % synodic_month
    if lunar_day_float < 0:
        lunar_day_float += synodic_month
    lunar_day = int(lunar_day_float) + 1
    if lunar_day > 30:
        lunar_day = 1
    lunar_day_str = LUNAR_DAY_NUMBERS[lunar_day] if lunar_day <= 30 else "初一"

    return f"{lunar_year_gan}{lunar_year_zhi}年{LUNAR_NUMBERS[lunar_month_num]}月{lunar_day_str}"


# =============================================================================
# 当前节气区间描述
# =============================================================================

def _get_current_jieqi_describe(month_idx: int) -> str:
    """返回当前月份节气区间描述字符串"""
    pairs = [
        ("立春", "惊蛰"), ("惊蛰", "清明"), ("清明", "立夏"),
        ("立夏", "芒种"), ("芒种", "小暑"), ("小暑", "立秋"),
        ("立秋", "白露"), ("白露", "寒露"), ("寒露", "立冬"),
        ("立冬", "大雪"), ("大雪", "小寒"), ("小寒", "立春"),
    ]
    if 0 <= month_idx < 12:
        s, e = pairs[month_idx]
        return f"{s}→{e}"
    return ""


# =============================================================================
# 主排盘函数
# =============================================================================

def paipan(solar_year: int, solar_month: int, solar_day: int,
           hour: int, minute: int = 0,
           longitude: float = 120.0, latitude: float = 30.0,
           gender: str = "男") -> Dict:
    """
    完整八字排盘。

    根据出生年月日时和经纬度，计算四柱天干地支，
    包含真太阳时矫正、藏干、纳音、节气等完整信息。

    参数:
        solar_year:  公历年 (如 1990)
        solar_month: 公历月 (1-12)
        solar_day:   公历日 (1-31)
        hour:        出生小时 北京时间 (0-23)
        minute:      出生分钟 (0-59)
        longitude:   出生地经度 (东经为正, 默认120=北京)
        latitude:    出生地纬度 (默认30)
        gender:      性别 ("男" 或 "女", 影响大运顺逆)

    返回:
        完整排盘结果字典，包含四柱、藏干、纳音、日主、节气等信息

    示例:
        >>> result = paipan(1990, 6, 15, 8, 30, 116.4, 39.9, "男")
        >>> print(result["day_master"])
        '戊'
    """
    # ---- 步骤1: 真太阳时矫正 ----
    day_offset, true_h, true_m = _calc_true_solar_time(
        solar_year, solar_month, solar_day, hour, minute, longitude
    )
    true_date = date(solar_year, solar_month, solar_day) + timedelta(days=day_offset)
    adj_year, adj_month, adj_day = true_date.year, true_date.month, true_date.day
    true_hour_float = true_h + true_m / 60.0

    # ---- 步骤2: 子时日期调整 (23:00后日柱算次日) ----
    dp_year, dp_month, dp_day = _adjust_for_zishi(adj_year, adj_month, adj_day, true_hour_float)

    # ---- 步骤3: 年柱 (以立春为界) ----
    bazi_year, year_gan, year_zhi = _calc_year_pillar(adj_year, adj_month, adj_day)

    # ---- 步骤4: 月柱 (年上起月法/五虎遁) ----
    month_idx, month_gan, month_zhi = _calc_month_pillar(adj_year, adj_month, adj_day, year_gan)

    # ---- 步骤5: 日柱 ----
    day_gan, day_zhi = _calc_day_pillar(dp_year, dp_month, dp_day)

    # ---- 步骤6: 时柱 (日上起时法/五鼠遁) ----
    hour_gan, hour_zhi, shichen = _calc_hour_pillar(true_hour_float, day_gan)

    # ---- 步骤7: 组装完整结果 ----
    y_ganzhi = year_gan + year_zhi
    m_ganzhi = month_gan + month_zhi
    d_ganzhi = day_gan + day_zhi
    h_ganzhi = hour_gan + hour_zhi

    y_nayin, y_nayin_wx = _get_nayin(year_gan, year_zhi)
    m_nayin, m_nayin_wx = _get_nayin(month_gan, month_zhi)
    d_nayin, d_nayin_wx = _get_nayin(day_gan, day_zhi)
    h_nayin, h_nayin_wx = _get_nayin(hour_gan, hour_zhi)

    y_canggan = _get_canggan(year_zhi)
    m_canggan = _get_canggan(month_zhi)
    d_canggan = _get_canggan(day_zhi)
    h_canggan = _get_canggan(hour_zhi)

    day_master = day_gan
    dm_wx = GAN_WUXING_LIST[_gan_index(day_gan)]

    try:
        from lunarcal.lunar_solar import solar_to_lunar
        lunar_info = solar_to_lunar(solar_year, solar_month, solar_day)
        lunar_year_str = f"{GAN[(lunar_info['lunar_year'] - 4) % 10]}{ZHI[(lunar_info['lunar_year'] - 4) % 12]}"
        lunar_month_num = lunar_info['lunar_month']
        lunar_day_num = lunar_info['lunar_day']
        is_leap = lunar_info.get('is_leap', False)
        month_str = LUNAR_NUMBERS[lunar_month_num]
        day_str = LUNAR_DAY_NUMBERS[lunar_day_num] if lunar_day_num <= 30 else '初一'
        leap_prefix = '闰' if is_leap else ''
        lunar_date = f"{lunar_year_str}年{leap_prefix}{month_str}月{day_str}"
    except Exception:
        lunar_date = _solar_to_lunar_approx(solar_year, solar_month, solar_day, bazi_year)

    true_h_int = int(true_h)
    true_m_int = int(round(true_m))
    if true_m_int >= 60:
        true_h_int += 1
        true_m_int -= 60
    true_solar_str = f"{true_h_int:02d}:{true_m_int:02d}"

    solar_date_str = f"{solar_year:04d}-{solar_month:02d}-{solar_day:02d}"
    solar_time_str = f"{hour:02d}:{minute:02d}"

    jieqi = _get_current_jieqi_describe(month_idx)

    result = {
        "birth_info": {
            "solar_date": solar_date_str,
            "solar_time": solar_time_str,
            "longitude": longitude,
            "latitude": latitude,
            "true_solar_time": true_solar_str,
            "lunar_date": lunar_date,
            "gender": gender,
            "bazi_year": bazi_year,
        },
        "four_pillars": {
            "year": {
                "gan": year_gan, "zhi": year_zhi,
                "ganzhi": y_ganzhi, "canggan": y_canggan,
                "nayin": y_nayin, "nayin_wuxing": y_nayin_wx,
            },
            "month": {
                "gan": month_gan, "zhi": month_zhi,
                "ganzhi": m_ganzhi, "canggan": m_canggan,
                "nayin": m_nayin, "nayin_wuxing": m_nayin_wx,
                "jieqi": jieqi,
            },
            "day": {
                "gan": day_gan, "zhi": day_zhi,
                "ganzhi": d_ganzhi, "canggan": d_canggan,
                "nayin": d_nayin, "nayin_wuxing": d_nayin_wx,
            },
            "hour": {
                "gan": hour_gan, "zhi": hour_zhi,
                "ganzhi": h_ganzhi, "canggan": h_canggan,
                "nayin": h_nayin, "nayin_wuxing": h_nayin_wx,
                "shichen": shichen,
            },
        },
        "day_master": day_master,
        "day_master_wuxing": dm_wx,
        "day_master_yinyang": GAN_YINYANG_LIST[_gan_index(day_gan)],
        "month_zhi": month_zhi,
        "month_zhi_wuxing": ZHI_WUXING_LIST[_zhi_index(month_zhi)],
        "year_gan": year_gan,
        "year_zhi": year_zhi,
    }

    # ---- 内联十神计算 (不依赖外部模块) ----
    def _inline_shishen(ri_gan, other_gan):
        ri_idx = GAN.index(ri_gan); ot_idx = GAN.index(other_gan)
        ri_wx = GAN_WUXING_LIST[ri_idx]; ot_wx = GAN_WUXING_LIST[ot_idx]
        same_yy = GAN_YINYANG_LIST[ri_idx] == GAN_YINYANG_LIST[ot_idx]
        if ri_wx == ot_wx: return '比肩' if same_yy else '劫财'
        wx_rel = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
        wx_k = {'木':'土','土':'水','水':'火','火':'金','金':'木'}
        if wx_rel.get(ri_wx) == ot_wx: return '食神' if same_yy else '伤官'
        if wx_k.get(ri_wx) == ot_wx: return '偏财' if same_yy else '正财'
        if wx_rel.get(ot_wx) == ri_wx: return '偏印' if same_yy else '正印'
        if wx_k.get(ot_wx) == ri_wx: return '七杀' if same_yy else '正官'
        return '未知'

    for pk in ['year', 'month', 'hour']:
        result['four_pillars'][pk]['shishen'] = _inline_shishen(day_master, result['four_pillars'][pk]['gan'])
    result['four_pillars']['day']['shishen'] = '日主'

    # ---- 追加分析结果 ----
    try:
        from algorithm.analysis import (
            count_wuxing, determine_strength, determine_geju,
            determine_yongji, calculate_dayun, calculate_liunian,
            generate_dayun_analysis
        )
        result['wuxing_count'] = count_wuxing(result['four_pillars'])
        result['strength'] = determine_strength(result['four_pillars'], day_master, month_zhi)
        result['geju'] = determine_geju(result['four_pillars'], day_master, month_zhi, result['strength'])
        result['yongji'] = determine_yongji(result['four_pillars'], day_master, result['strength'], result['geju'], month_zhi)
        solar_birth = datetime(solar_year, solar_month, solar_day, hour, minute)
        result['dayun'] = calculate_dayun(solar_birth, result['four_pillars'], gender)
        result['dayun']['dayun_list'] = generate_dayun_analysis(
            result['four_pillars'], day_master, result['dayun']['dayun_list'],
            result['yongji'], result['strength'], month_zhi
        )
        result['dayun']['liunian_current'] = calculate_liunian(result['four_pillars'], result['dayun'], datetime.now().year, day_master)
    except Exception as e:
        import traceback; traceback.print_exc()
        result['wuxing_count'] = {'金':{'count':0,'score':0},'木':{'count':0,'score':0},'水':{'count':0,'score':0},'火':{'count':0,'score':0},'土':{'count':0,'score':0}}
        result['strength'] = {'level':'未知','score':0,'details':'分析模块加载失败'}
        result['geju'] = {'type':'未知','name':'未知','analysis':''}
        result['yongji'] = {'yong_shen':[],'ji_shen':[],'xian_shen':[],'tiao_hou':''}
        result['dayun'] = {'start_age':0,'direction':'','dayun_list':[],'current_dayun':{},'liunian_current':{}}

    # ---- 神煞/十二长生/胎元命宫/空亡/干支关系 ----
    try:
        from algorithm.shensha import (
            calc_all_shensha, calc_12_changsheng, get_changsheng_for_zhi,
            calc_taiyuan, calc_minggong, calc_shengong, calc_kongwang,
            calc_wuxing_season_state, analyze_zhi_relations
        )
        # 神煞
        result['shensha'] = calc_all_shensha(
            result['four_pillars'], day_master,
            result['year_zhi'], month_zhi, gender
        )
        # 十二长生
        result['changsheng'] = {}
        cs = calc_12_changsheng(day_master)
        for pk, pl in result['four_pillars'].items():
            result['changsheng'][pk] = {'zhi': pl['zhi'], 'state': cs.get(pl['zhi'], '')}
        # 胎元
        result['taiyuan'] = calc_taiyuan(result['four_pillars']['month']['ganzhi'])
        # 命宫
        result['minggong'] = calc_minggong(month_zhi, result['four_pillars']['hour']['zhi'])
        # 身宫
        result['shengong'] = calc_shengong(result['minggong'], result['four_pillars']['month']['gan'])
        # 空亡
        kw1, kw2 = calc_kongwang(result['four_pillars']['day']['ganzhi'])
        result['kongwang'] = [kw1, kw2]
        # 五行旺相休囚死
        result['wuxing_season'] = calc_wuxing_season_state(month_zhi)
        # 地支关系
        result['zhi_relations'] = analyze_zhi_relations(result['four_pillars'])
    except Exception:
        result['shensha'] = {}
        result['changsheng'] = {}
        result['taiyuan'] = ''
        result['minggong'] = ''
        result['shengong'] = ''
        result['kongwang'] = []
        result['wuxing_season'] = {}
        result['zhi_relations'] = {}

    return result


# =============================================================================
# 便捷函数
# =============================================================================

def get_solar_terms_for_year(year: int) -> List[Dict]:
    """
    获取指定年份的所有 24 节气日期。

    返回:
        [{"name": "立春", "date": "2024-02-04", "is_jie": True}, ...]
    """
    terms = []
    for i in range(24):
        y, m, d = _get_solar_term_date(year, i)
        terms.append({
            "name": SOLAR_TERM_NAMES[i],
            "date": f"{y:04d}-{m:02d}-{d:02d}",
            "is_jie": i in JIE_INDICES,
        })
    return terms


def get_lichun_date(year: int) -> str:
    """获取指定年份的立春日期"""
    y, m, d = _get_solar_term_date(year, 2)
    return f"{y:04d}-{m:02d}-{d:02d}"
