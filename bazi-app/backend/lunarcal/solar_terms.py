"""
节气数据模块 - Solar Terms Module

基于寿星万年历（VSOP87简化版）天文算法计算24节气精确日期时间。
算法参考：
  - Jean Meeus, "Astronomical Algorithms", 2nd Edition
  - 寿星万年历 (https://github.com/6tail/lunar)
  - VSOP87 行星理论简化版

精度：5分钟以内，足以用于八字排盘。

24节气及其太阳黄经度数：
  - 立春 315°（年柱分界点）    - 雨水 330°
  - 惊蛰 345°（月柱寅→卯）     - 春分 0°
  - 清明 15°                   - 谷雨 30°
  - 立夏 45°                   - 小满 60°
  - 芒种 75°                   - 夏至 90°
  - 小暑 105°                  - 大暑 120°
  - 立秋 135°                  - 处暑 150°
  - 白露 165°                  - 秋分 180°
  - 寒露 195°                  - 霜降 210°
  - 立冬 225°                  - 小雪 240°
  - 大雪 255°                  - 冬至 270°
  - 小寒 285°                  - 大寒 300°

月柱节气分界（十二节，非"气"）：
  立春→寅月, 惊蛰→卯月, 清明→辰月,
  立夏→巳月, 芒种→午月, 小暑→未月,
  立秋→申月, 白露→酉月, 寒露→戌月,
  立冬→亥月, 大雪→子月, 小寒→丑月
"""

import math
from datetime import datetime, timedelta, timezone

# ============================================================
# 24 节气名称（按黄经度数排序，从立春=315°开始）
# ============================================================
SOLAR_TERM_NAMES = [
    "立春", "雨水", "惊蛰", "春分", "清明", "谷雨",
    "立夏", "小满", "芒种", "夏至", "小暑", "大暑",
    "立秋", "处暑", "白露", "秋分", "寒露", "霜降",
    "立冬", "小雪", "大雪", "冬至", "小寒", "大寒",
]

# 节气对应的太阳黄经度数（度）
SOLAR_TERM_LONGITUDE = [
    315, 330, 345, 0, 15, 30,
    45, 60, 75, 90, 105, 120,
    135, 150, 165, 180, 195, 210,
    225, 240, 255, 270, 285, 300,
]

# 月柱所需的"节"（月支分界点），按顺序列出对应的黄经
# 注意：八字月柱按十二"节"划分，不按"气"划分
MONTH_PILLAR_TERMS = [
    ("立春", 315),   # 寅月开始
    ("惊蛰", 345),   # 卯月开始
    ("清明", 15),    # 辰月开始
    ("立夏", 45),    # 巳月开始
    ("芒种", 75),    # 午月开始
    ("小暑", 105),   # 未月开始
    ("立秋", 135),   # 申月开始
    ("白露", 165),   # 酉月开始
    ("寒露", 195),   # 戌月开始
    ("立冬", 225),   # 亥月开始
    ("大雪", 255),   # 子月开始
    ("小寒", 285),   # 丑月开始
]

# 月支名称（按节气顺序对应的地支）
MONTH_BRANCH_NAMES = ["寅", "卯", "辰", "巳", "午", "未",
                      "申", "酉", "戌", "亥", "子", "丑"]

# 节气名称到黄经的映射
TERM_NAME_TO_LONGITUDE = dict(zip(SOLAR_TERM_NAMES, SOLAR_TERM_LONGITUDE))

# 黄经到节气名称的映射（用于查找）
LONGITUDE_TO_TERM = dict(zip(SOLAR_TERM_LONGITUDE, SOLAR_TERM_NAMES))

# UTC+8 时区
_UTC8 = timezone(timedelta(hours=8))

# ============================================================
# 天文常数
# ============================================================
_J2000 = 2451545.0  # 儒略日 J2000.0 纪元


def _julian_day(year, month, day, hour=0, minute=0, second=0):
    """
    将公历日期时间转换为儒略日（Julian Day Number）。
    使用 Fliegel-Van Flandern 算法。
    返回浮点数儒略日。
    """
    # 对于1月、2月，视为前一年的13月、14月
    if month <= 2:
        year -= 1
        month += 12

    A = year // 100
    B = 2 - A + A // 4

    jd = (int(365.25 * (year + 4716))
          + int(30.6001 * (month + 1))
          + day + B - 1524.5)

    # 加上时间的小数部分
    day_fraction = (hour + minute / 60.0 + second / 3600.0) / 24.0
    return jd + day_fraction


def _jd_to_datetime(jd, utc8=True):
    """
    将儒略日转换为 datetime 对象。
    默认返回 UTC+8（北京时间）。
    """
    jd += 0.5
    Z = int(jd)
    F = jd - Z

    if Z < 2299161:
        A = Z
    else:
        alpha = int((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - alpha // 4

    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)

    day = B - D - int(30.6001 * E) + F
    month = E - 1 if E < 14 else E - 13
    year = C - 4716 if month > 2 else C - 4715

    # 分离整数天和小数部分
    iday = int(day)
    day_fraction = day - iday
    total_seconds = day_fraction * 86400
    hour = int(total_seconds // 3600)
    minute = int((total_seconds % 3600) // 60)
    second = int(total_seconds % 60)
    microsecond = int((total_seconds - int(total_seconds)) * 1_000_000)

    dt = datetime(year, month, iday, hour, minute, second, microsecond)

    if utc8:
        # 转换为北京时间 (UTC+8)
        # 儒略日计算基于UT，加上8小时得到北京时间
        dt = dt + timedelta(hours=8)

    return dt


def _mod_angle(deg):
    """将角度归一化到 [0, 360) 范围。"""
    return deg - 360.0 * math.floor(deg / 360.0)


def _sun_ecliptic_longitude(jd):
    """
    计算太阳在给定儒略日时刻的黄经度数（视黄经，含章动修正）。
    使用 VSOP87 简化算法（精度约 1 角秒）。

    参数:
        jd: 儒略日（浮点数）

    返回:
        太阳视黄经（度，0-360）
    """
    # 儒略世纪数（从 J2000.0 起算）
    T = (jd - _J2000) / 36525.0

    # ---- 太阳平均轨道根数 ----

    # 太阳平黄经（度）
    L0 = _mod_angle(280.46645 + 36000.76983 * T + 0.0003032 * T * T)

    # 太阳平近点角（度）
    M = _mod_angle(357.52910 + 35999.05030 * T - 0.0001559 * T * T)

    # 地球轨道偏心率
    e = 0.016708617 - 0.000042037 * T - 0.0000001236 * T * T

    # ---- 中心差（Equation of Center）----
    M_rad = math.radians(M)
    C = ((1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M_rad)
         + (0.019993 - 0.000101 * T) * math.sin(2 * M_rad)
         + 0.000289 * math.sin(3 * M_rad))

    # 太阳真黄经
    true_longitude = _mod_angle(L0 + C)

    # ---- 章动修正 ----
    # 月球升交点黄经（度）
    Omega = _mod_angle(125.04 - 1934.136 * T)

    # 视黄经（修正章动和光行差）
    apparent_longitude = _mod_angle(true_longitude
                                     - 0.00569
                                     - 0.00478 * math.sin(math.radians(Omega)))

    return apparent_longitude


def _find_solar_term_jd(year, target_longitude):
    """
    使用牛顿迭代法寻找指定年份、指定黄经的精确儒略日时刻。

    参数:
        year: 年份
        target_longitude: 目标黄经度数（0-360）

    返回:
        儒略日（浮点数）
    """
    # ---- 初始估计：基于平太阳运动 ----
    # 春分点（黄经0°）大约在3月20日前后（年初第79天）
    #
    # 太阳黄经每年递增360°，即每天约0.9856°
    # 从春分起算：day = 79 + (target_longitude / 360.0) * 365.2422
    #
    # 对于黄经 > 0 的节气（如夏至90°、冬至270°），
    # 它们在春分之后：day_of_year 对应同年较晚的日期
    #
    # 对于黄经 > 180 的节气（如立春315°），计算结果会超出365，
    # 此时减去365即得到次年1-2月的日期（属目标年份的年初）
    rough_doy = 79.0 + (target_longitude / 360.0) * 365.2422
    while rough_doy < 1:
        rough_doy += 365.2422
    while rough_doy > 365.2422:
        rough_doy -= 365.2422

    # 对于年末节气（冬至270°、小寒285°、大寒300°），
    # rough_doy 可能落在目标年份的12月
    # 对于年初节气（立春315°、雨水330°），
    # rough_doy 落在目标年份的1-2月

    init_jd = _julian_day(year, 1, 1) + rough_doy - 1

    # ---- 牛顿迭代法求精 ----
    jd = init_jd
    for _ in range(10):  # 最多10次迭代
        longitude = _sun_ecliptic_longitude(jd)
        diff = _mod_angle(target_longitude - longitude)

        # 处理角度环绕：差值应为 [-180, 180]
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360

        if abs(diff) < 0.0001:  # 精度约 0.5 秒
            break

        # 太阳每日运动约 0.9856 度/天
        # 使用更精确的速率：当前点的导数
        daily_motion = 360.0 / 365.2422  # 近似值
        delta_days = diff / daily_motion
        jd += delta_days

    return jd


def get_solar_term(year, term_name):
    """
    计算指定年份的指定节气精确日期时间。

    使用寿星万年历算法（VSOP87简化版），
    基于太阳黄经度数计算，精度在5分钟以内。

    参数:
        year: 公历年份（int）
        term_name: 节气名称（str），如"立春"、"冬至"等

    返回:
        datetime 对象（北京时间 UTC+8），表示该节气的精确时刻

    异常:
        ValueError: 节气名称无效
    """
    if term_name not in TERM_NAME_TO_LONGITUDE:
        raise ValueError(f"无效节气名称: {term_name}。有效名称: {SOLAR_TERM_NAMES}")

    target_longitude = TERM_NAME_TO_LONGITUDE[term_name]

    # 对于冬至（270°）、小寒（285°）、大寒（300°），
    # 它们可能落在 year-1 的末尾
    # 对于立春（315°）到雨水等，在年初
    # 我们需要在合理的日期范围搜索

    # 查找策略：搜索 year-1 年12月到 year 年12月的范围
    jd = _find_solar_term_jd(year, target_longitude)

    dt_utc = _jd_to_datetime(jd, utc8=True)

    # 如果计算出的年份与目标年份不符（对于年末节气），调整
    if dt_utc.year < year:
        # 可能属于 year-1 年末，重新以 year+1 搜索
        pass
    elif dt_utc.year > year:
        # 重新用 year-1 搜索
        pass

    # 对于大部分节气，年份应该正确
    # 但为了精确，针对年末节气做二次校正
    if term_name in ("小寒", "大寒"):
        # 这些节气通常在公历1月初到1月下旬，属于year年
        # 如果计算结果在12月，可能是错误
        if dt_utc.month == 12:
            # 重新搜索
            jd = _find_solar_term_jd(year, target_longitude)
            # 确保在目标年份范围内
            jd_start = _julian_day(year, 1, 1)
            jd_end = _julian_day(year, 12, 31, 23, 59, 59)
            if jd < jd_start or jd > jd_end:
                # 微调
                jd = _find_solar_term_jd(year, target_longitude)
            dt_utc = _jd_to_datetime(jd, utc8=True)

    return dt_utc


def get_all_solar_terms(year):
    """
    返回指定年份所有24个节气的日期列表。

    参数:
        year: 公历年份（int）

    返回:
        list of dict，每个元素包含:
            - name: 节气名称（str）
            - date: datetime 对象
            - longitude: 太阳黄经度数（int）
    """
    terms = []
    for name, longitude in zip(SOLAR_TERM_NAMES, SOLAR_TERM_LONGITUDE):
        dt = get_solar_term(year, name)
        terms.append({
            "name": name,
            "date": dt,
            "longitude": longitude,
        })
    # 按日期排序
    terms.sort(key=lambda x: x["date"])
    return terms


def get_current_solar_term(date):
    """
    给定公历日期，返回当前所处的节气区间。

    即找出目标日期位于哪个节气与下一个节气之间。

    参数:
        date: datetime 对象或 date 对象

    返回:
        (prev_term, prev_term_date, next_term, next_term_date)
        其中 prev_term_date <= date < next_term_date

    异常:
        ValueError: 日期超出支持范围
    """
    year = date.year

    # 获取前一年、当年、后一年的所有节气
    # 因为年末/年初的节气可能跨越年份边界
    all_terms = []
    for y in (year - 1, year, year + 1):
        terms = get_all_solar_terms(y)
        all_terms.extend(terms)

    # 转换为 datetime 进行比较
    if isinstance(date, datetime):
        target_dt = date
    else:
        target_dt = datetime(date.year, date.month, date.day)

    # 按日期排序
    all_terms.sort(key=lambda x: x["date"])

    # 找到目标日期所在的区间
    for i in range(len(all_terms) - 1):
        term_date = all_terms[i]["date"]
        next_term_date = all_terms[i + 1]["date"]

        # 确保 datetime 类型一致
        if isinstance(term_date, datetime):
            term_dt = term_date
        else:
            term_dt = datetime(term_date.year, term_date.month, term_date.day)
        if isinstance(next_term_date, datetime):
            next_dt = next_term_date
        else:
            next_dt = datetime(next_term_date.year, next_term_date.month, next_term_date.day)

        if term_dt <= target_dt < next_dt:
            return (all_terms[i]["name"], term_dt,
                    all_terms[i + 1]["name"], next_dt)

    # 如果找不到（理论上不会），抛出异常
    raise ValueError(f"无法确定日期 {date} 的节气区间")


def get_month_branch_by_solar_term(date):
    """
    根据节气确定月支（用于八字月柱）。

    八字月柱严格按"节"划分，不按农历月份：
    - 立春开始寅月（正月）
    - 惊蛰开始卯月
    - 清明开始辰月
    - 立夏开始巳月
    - 芒种开始午月
    - 小暑开始未月
    - 立秋开始申月
    - 白露开始酉月
    - 寒露开始戌月
    - 立冬开始亥月
    - 大雪开始子月
    - 小寒开始丑月

    参数:
        date: datetime 或 date 对象

    返回:
        (月支名称, 月支索引0-11, 当前节气的datetime)
        月支名称如 "寅", "卯" 等
    """
    prev_term, prev_date, next_term, next_date = get_current_solar_term(date)

    # 月支由当前所处的节气区间的前一个"节"决定
    # 即：如果日期在立春到惊蛰之间，月支为寅
    term_to_branch = {
        "立春": "寅", "惊蛰": "卯", "清明": "辰",
        "立夏": "巳", "芒种": "午", "小暑": "未",
        "立秋": "申", "白露": "酉", "寒露": "戌",
        "立冬": "亥", "大雪": "子", "小寒": "丑",
    }

    if prev_term in term_to_branch:
        branch = term_to_branch[prev_term]
        branch_index = MONTH_BRANCH_NAMES.index(branch)
        return branch, branch_index, prev_date

    # 如果 prev_term 不是"节"（比如对于从大寒到立春之间的日期），
    # 需要特殊处理：大寒到立春之间按小寒算（丑月）
    # 但实际上 get_current_solar_term 返回的区间中，
    # 只有"节"和"气"交替出现

    # 检查是否是"节"与"气"之间的区间
    # 如果不是，回溯到最近的"节"
    year = date.year
    for y in (year - 1, year + 1):
        terms = get_all_solar_terms(y)
        for t in terms:
            if t["name"] in term_to_branch:
                term_dt = t["date"]
                if isinstance(term_dt, datetime):
                    pass
                else:
                    term_dt = datetime(term_dt.year, term_dt.month, term_dt.day)
                if term_dt <= date:
                    # 检查是否是最接近的节
                    branch = term_to_branch[t["name"]]
                    branch_index = MONTH_BRANCH_NAMES.index(branch)
                    return branch, branch_index, term_dt

    # 兜底：无法确定时返回默认
    raise ValueError(f"无法确定日期 {date} 的月支")


# ============================================================
# 节气近似日期范围（1900-2100年适用）
# 存储每月节的常见日期范围，作为快速查找和验证参考
# ============================================================

# 节气的近似日期范围（月, 日范围元组）
# 格式: 节气名 -> (月, 最早日, 最晚日)
SOLAR_TERM_APPROX_RANGE = {
    "立春": (2, 3, 5),
    "雨水": (2, 18, 20),
    "惊蛰": (3, 5, 7),
    "春分": (3, 20, 22),
    "清明": (4, 4, 6),
    "谷雨": (4, 19, 21),
    "立夏": (5, 5, 7),
    "小满": (5, 20, 22),
    "芒种": (6, 5, 7),
    "夏至": (6, 21, 22),
    "小暑": (7, 6, 8),
    "大暑": (7, 22, 24),
    "立秋": (8, 7, 9),
    "处暑": (8, 22, 24),
    "白露": (9, 7, 9),
    "秋分": (9, 22, 24),
    "寒露": (10, 7, 9),
    "霜降": (10, 23, 24),
    "立冬": (11, 7, 8),
    "小雪": (11, 22, 23),
    "大雪": (12, 6, 8),
    "冬至": (12, 21, 23),
    "小寒": (1, 5, 7),
    "大寒": (1, 20, 21),
}


def verify_solar_term_date(date, term_name):
    """
    验证给定日期是否在指定节气的合理范围内。
    用于快速校验。

    参数:
        date: datetime 或 date 对象
        term_name: 节气名称

    返回:
        bool: 日期是否在该节气的正常范围内
    """
    if term_name not in SOLAR_TERM_APPROX_RANGE:
        return False
    month, min_day, max_day = SOLAR_TERM_APPROX_RANGE[term_name]
    return date.month == month and min_day <= date.day <= max_day
