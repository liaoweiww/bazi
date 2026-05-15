"""
月柱计算模块 - Month Pillar Calculation

八字四柱中的月柱计算。月柱严格按24节气中的十二"节"划分，
而非农历月份。这是八字排盘的核心规则。

月支对照表（十二节 → 十二月支）:
  ============ ======== ================
  节气(节)      月支      公历约期
  ============ ======== ================
  立春 315°    寅(虎)    2月4日前后
  惊蛰 345°    卯(兔)    3月6日前后
  清明 15°     辰(龙)    4月5日前后
  立夏 45°     巳(蛇)    5月6日前后
  芒种 75°     午(马)    6月6日前后
  小暑 105°    未(羊)    7月7日前后
  立秋 135°    申(猴)    8月8日前后
  白露 165°    酉(鸡)    9月8日前后
  寒露 195°    戌(狗)    10月8日前后
  立冬 225°    亥(猪)    11月7日前后
  大雪 255°    子(鼠)    12月7日前后
  小寒 285°    丑(牛)    1月6日前后
  ============ ======== ================

年上起月法（五虎遁）:
  根据年柱天干确定寅月(正月)的天干:
    甲己之年 → 丙寅开始 (丙作首)
    乙庚之年 → 戊寅开始 (戊为头)
    丙辛之年 → 庚寅开始 (庚起)
    丁壬之年 → 壬寅开始 (壬顺流)
    戊癸之年 → 甲寅开始 (甲配戊癸)

  口诀:
    "甲己之年丙作首, 乙庚之岁戊为头,
     丙辛必定寻庚起, 丁壬壬位顺行流,
     若问戊癸何方发, 甲寅之上好追求。"

日上起时法（五鼠遁）:
  根据日柱天干确定子时的天干:
    甲己日 → 甲子时开始
    乙庚日 → 丙子时开始
    丙辛日 → 戊子时开始
    丁壬日 → 庚子时开始
    戊癸日 → 壬子时开始

  口诀:
    "甲己还加甲, 乙庚丙作初,
     丙辛从戊起, 丁壬庚子居,
     戊癸何方发, 壬子是真途。"

算法验证参考:
  - 2024年甲辰年: 寅月起丙寅(正月), 卯月丁卯(二月)...
  - 2025年乙巳年立春后: 寅月起戊寅
"""

from datetime import date, datetime, timedelta

__all__ = [
    "get_month_pillar",
    "get_hour_pillar",
    "get_month_branch_by_date",
    "get_day_gan_by_hour_gan",
    "get_hour_branch_by_time",
    "TIANGAN",
    "DIZHI",
]

# ============================================================
# 天干地支
# ============================================================
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def _gan_index(gan_char):
    """天干字符转0-based索引。"""
    return TIANGAN.index(gan_char)


def _zhi_index(zhi_char):
    """地支字符转0-based索引。"""
    return DIZHI.index(zhi_char)


# ============================================================
# 节气 → 月支 映射
# ============================================================
# 十二"节"名称及其对应的月支(0-based索引)
_SOLAR_TERM_TO_MONTH_BRANCH = {
    "立春": ("寅", 2),    # 立春 → 寅月
    "惊蛰": ("卯", 3),    # 惊蛰 → 卯月
    "清明": ("辰", 4),    # 清明 → 辰月
    "立夏": ("巳", 5),    # 立夏 → 巳月
    "芒种": ("午", 6),    # 芒种 → 午月
    "小暑": ("未", 7),    # 小暑 → 未月
    "立秋": ("申", 8),    # 立秋 → 申月
    "白露": ("酉", 9),    # 白露 → 酉月
    "寒露": ("戌", 10),   # 寒露 → 戌月
    "立冬": ("亥", 11),   # 立冬 → 亥月
    "大雪": ("子", 0),    # 大雪 → 子月
    "小寒": ("丑", 1),    # 小寒 → 丑月
}

# ============================================================
# 五虎遁: 年干 → 寅月天干起始
# ============================================================
# 年干索引 → 寅月天干索引 的偏移
# 公式: month_stem_index = (month_branch_index + _MONTH_STEM_BASE[year_gan_index]) % 10
# 其中 _MONTH_STEM_BASE 是寅月(月支=2)的天干在年干下的索引

# 推导: 对于年干 y:
#   甲(0)己(5) → 寅月为丙(2): base[0]=base[5]=(2-2)%10=0
#   乙(1)庚(6) → 寅月为戊(4): base[1]=base[6]=(4-2)%10=2
#   丙(2)辛(7) → 寅月为庚(6): base[2]=base[7]=(6-2)%10=4
#   丁(3)壬(8) → 寅月为壬(8): base[3]=base[8]=(8-2)%10=6
#   戊(4)癸(9) → 寅月为甲(0): base[4]=base[9]=(0-2)%10=8

_WU_HU_DUN_OFFSET = {
    0: 0,   # 甲年 → 丙寅 (stem offset = 2), base = (2-2)%10 = 0
    1: 2,   # 乙年 → 戊寅 (stem offset = 4), base = (4-2)%10 = 2
    2: 4,   # 丙年 → 庚寅 (stem offset = 6), base = (6-2)%10 = 4
    3: 6,   # 丁年 → 壬寅 (stem offset = 8), base = (8-2)%10 = 6
    4: 8,   # 戊年 → 甲寅 (stem offset = 0), base = (0-2)%10 = 8
    5: 0,   # 己年 → 丙寅 (同甲)
    6: 2,   # 庚年 → 戊寅 (同乙)
    7: 4,   # 辛年 → 庚寅 (同丙)
    8: 6,   # 壬年 → 壬寅 (同丁)
    9: 8,   # 癸年 → 甲寅 (同戊)
}


def _wu_hu_dun_offset(year_gan_index):
    """
    五虎遁: 根据年干计算月干起始偏移。
    返回: 寅月的天干索引
    """
    return _WU_HU_DUN_OFFSET.get(year_gan_index, 0)


# ============================================================
# 五鼠遁: 日干 → 子时天干起始
# ============================================================
# 日干索引 → 子时天干索引
# 甲(0)己(5) → 甲子(0): stem=0
# 乙(1)庚(6) → 丙子(2): stem=2
# 丙(2)辛(7) → 戊子(4): stem=4
# 丁(3)壬(8) → 庚子(6): stem=6
# 戊(4)癸(9) → 壬子(8): stem=8

_WU_SHU_DUN_BASE = {
    0: 0,   # 甲 → 甲子
    1: 2,   # 乙 → 丙子
    2: 4,   # 丙 → 戊子
    3: 6,   # 丁 → 庚子
    4: 8,   # 戊 → 壬子
    5: 0,   # 己 → 甲子 (同甲)
    6: 2,   # 庚 → 丙子 (同乙)
    7: 4,   # 辛 → 戊子 (同丙)
    8: 6,   # 壬 → 庚子 (同丁)
    9: 8,   # 癸 → 壬子 (同戊)
}


def _wu_shu_dun_base_gan(day_gan_index):
    """五鼠遁: 根据日干计算子时起始天干索引。"""
    return _WU_SHU_DUN_BASE.get(day_gan_index, 0)


# ============================================================
# 时辰 → 地支 映射
# ============================================================
# 时辰划分（以真太阳时为准）:
#   子时: 23:00 - 00:59  (注意跨日!)
#   丑时: 01:00 - 02:59
#   寅时: 03:00 - 04:59
#   卯时: 05:00 - 06:59
#   辰时: 07:00 - 08:59
#   巳时: 09:00 - 10:59
#   午时: 11:00 - 12:59
#   未时: 13:00 - 14:59
#   申时: 15:00 - 16:59
#   酉时: 17:00 - 18:59
#   戌时: 19:00 - 20:59
#   亥时: 21:00 - 22:59

# 每个时辰对应2小时，共12个时辰
# 地支顺序: 子丑寅卯辰巳午未申酉戌亥

_HOUR_TO_BRANCH = [
    "子",  # 0时 (含23时)
    "丑",  # 1-2时
    "丑",
    "寅",  # 3-4时
    "寅",
    "卯",  # 5-6时
    "卯",
    "辰",  # 7-8时
    "辰",
    "巳",  # 9-10时
    "巳",
    "午",  # 11-12时
    "午",
    "未",  # 13-14时
    "未",
    "申",  # 15-16时
    "申",
    "酉",  # 17-18时
    "酉",
    "戌",  # 19-20时
    "戌",
    "亥",  # 21-22时
    "亥",
    "子",  # 23时 (与0时间属子时)
]

# 时辰地支索引 (0-based, 子=0)
_HOUR_TO_BRANCH_INDEX = [DIZHI.index(b) for b in _HOUR_TO_BRANCH]


def get_hour_branch(hour):
    """
    根据小时(0-23)获取时辰地支。

    参数:
        hour: int, 0-23

    返回:
        str: 地支名称, 如 "子", "丑"等

    示例:
        hour=0  → "子" (23:00-00:59)
        hour=12 → "午" (11:00-12:59)
        hour=23 → "子" (23:00-00:59)
    """
    if hour < 0 or hour > 23:
        raise ValueError(f"小时必须在 0-23 之间, 收到 {hour}")
    return _HOUR_TO_BRANCH[hour]


def get_hour_branch_index(hour):
    """
    根据小时获取时辰地支的索引 (0-11, 子=0)。

    参数:
        hour: int, 0-23

    返回:
        int: 0-11
    """
    if hour < 0 or hour > 23:
        raise ValueError(f"小时必须在 0-23 之间, 收到 {hour}")
    return _HOUR_TO_BRANCH_INDEX[hour]


def get_hour_branch_by_time(dt):
    """
    根据 datetime 对象获取时辰地支。

    八字日柱以子时(23:00)为日分界点:
    - 23:00 之后属于次日
    - 但时辰地支仍为 "子"

    参数:
        dt: datetime 对象

    返回:
        (branch_name, branch_index):
            branch_name: str, 地支名称
            branch_index: int, 0-11
    """
    hour = dt.hour
    branch_name = get_hour_branch(hour)
    branch_index = get_hour_branch_index(hour)
    return branch_name, branch_index


# ============================================================
# 月柱计算
# ============================================================

def get_month_pillar(year, solar_term_date):
    """
    根据年柱和节气日期计算月柱。

    月柱严格按节气划分:
      立春 → 寅月, 惊蛰 → 卯月, 清明 → 辰月,
      立夏 → 巳月, 芒种 → 午月, 小暑 → 未月,
      立秋 → 申月, 白露 → 酉月, 寒露 → 戌月,
      立冬 → 亥月, 大雪 → 子月, 小寒 → 丑月。

    年上起月法（五虎遁）:
      甲己之年丙作首 → 寅月天干 = 丙
      乙庚之岁戊为头 → 寅月天干 = 戊
      丙辛必定寻庚起 → 寅月天干 = 庚
      丁壬壬位顺行流 → 寅月天干 = 壬
      若问戊癸何方发 → 寅月天干 = 甲
      甲寅之上好追求

    天干计算公式:
      month_stem_index = (month_branch_index + year_stem_offset) % 10
      其中 year_stem_offset = (year_gan_index % 5) * 2

    参数:
        year: 八字年柱所在的公历年（用于确定年柱天干）
        solar_term_date: 日期（date 或 datetime），或节气名称（str）
                         如果是节气名称，如"立春"、"惊蛰"等

    返回:
        (天干, 地支): 如 ("丙", "寅") 表示丙寅月

    异常:
        ValueError: 无法确定月支或节气名称无效

    示例:
        >>> # 2024年甲辰年, 立春后的寅月 → 丙寅月
        >>> get_month_pillar(2024, "立春")
        ("丙", "寅")

        >>> # 2025年乙巳年, 芒种后的午月 → 壬午月
        >>> get_month_pillar(2025, "芒种")
        ("壬", "午")

        >>> # 2024年甲辰年, 4月1日 (春分后, 清明前 → 卯月)
        >>> get_month_pillar(2024, date(2024, 4, 1))
        ("丁", "卯")
    """
    # ---- 确定月支 ----
    if isinstance(solar_term_date, str):
        # 直接给定节气名称
        term_name = solar_term_date
        if term_name not in _SOLAR_TERM_TO_MONTH_BRANCH:
            raise ValueError(f"无效的节气名称: {term_name}。"
                             f"有效的节: {list(_SOLAR_TERM_TO_MONTH_BRANCH.keys())}")
        month_zhi, month_zhi_idx = _SOLAR_TERM_TO_MONTH_BRANCH[term_name]
    else:
        # 给定日期，需要查找该日期所属的节
        # 导入 solar_terms 模块来确定
        from .solar_terms import (
            get_current_solar_term,
            MONTH_BRANCH_NAMES,
        )

        prev_term, prev_date, next_term, next_date = get_current_solar_term(solar_term_date)

        # prev_term 是当前区间的起始节气（可能是"节"也可能是"气"）
        # 月支由最近的"节"决定
        if prev_term in _SOLAR_TERM_TO_MONTH_BRANCH:
            month_zhi, month_zhi_idx = _SOLAR_TERM_TO_MONTH_BRANCH[prev_term]
        else:
            # prev_term 是"气"（如雨水、春分等），需要回溯到上一个"节"
            # 查找所有节气日期，找到最近的一个"节"
            from .solar_terms import get_all_solar_terms
            all_terms = get_all_solar_terms(year)

            # 也需要查前一年的（年末节气跨年）
            try:
                prev_year_terms = get_all_solar_terms(year - 1)
                all_terms = prev_year_terms + all_terms
            except Exception:
                pass

            all_terms.sort(key=lambda x: x["date"])

            # 转换为 datetime
            if isinstance(solar_term_date, datetime):
                target = solar_term_date
            else:
                target = datetime(solar_term_date.year, solar_term_date.month,
                                  solar_term_date.day)

            # 从后往前找最近的"节"
            found = None
            for t in reversed(all_terms):
                if t["name"] not in _SOLAR_TERM_TO_MONTH_BRANCH:
                    continue
                t_date = t["date"]
                if isinstance(t_date, datetime):
                    t_dt = t_date
                else:
                    t_dt = datetime(t_date.year, t_date.month, t_date.day)
                if t_dt <= target:
                    found = t
                    break

            if found is None:
                raise ValueError(f"无法确定日期 {solar_term_date} 的月支")

            month_zhi, month_zhi_idx = _SOLAR_TERM_TO_MONTH_BRANCH[found["name"]]

    # ---- 确定月干 ----
    # 先确定年干
    # 八字年柱以立春为界
    from .solar_terms import get_solar_term

    lichun = get_solar_term(year, "立春")
    if isinstance(lichun, datetime):
        lichun_d = lichun.date()
    else:
        lichun_d = lichun

    # 确定年柱所在的年干
    if isinstance(solar_term_date, str):
        # 如果给的是节气名，需要判断年份
        # 对于大雪(12月)、小寒(1月)、大寒(1月): 若传入的year是基于公历年
        # 小寒、大寒通常在公历1月，属于上一个农历年(八字年)
        if solar_term_date in ("小寒", "大寒"):
            # 小寒大寒通常在下一年公历1月，八字年仍为year-1

            from .lunar_solar import _compute_year_ganzhi_index
            reference_gan_index = _compute_year_ganzhi_index(year - 1) % 10
        elif solar_term_date in ("立春", "雨水"):
            # 立春/雨水: 八字年可能是year-1或year
            # 简化处理: 取year的立春日期，在立春之后的立春属于year年
            from .lunar_solar import _compute_year_ganzhi_index
            reference_gan_index = _compute_year_ganzhi_index(year) % 10
        else:
            from .lunar_solar import _compute_year_ganzhi_index
            reference_gan_index = _compute_year_ganzhi_index(year) % 10
    else:
        # 日期: 比较立春日期
        if isinstance(solar_term_date, datetime):
            target_d = solar_term_date.date()
        else:
            target_d = solar_term_date

        if target_d >= lichun_d:
            # 在立春当天或之后
            from .lunar_solar import _compute_year_ganzhi_index
            reference_gan_index = _compute_year_ganzhi_index(year) % 10
        else:
            # 在立春之前 → 属于上一年
            from .lunar_solar import _compute_year_ganzhi_index
            reference_gan_index = _compute_year_ganzhi_index(year - 1) % 10

    # 五虎遁公式:
    # month_stem_index = (month_branch_index + (year_gan % 5) * 2) % 10
    # 验证: 甲年(0), 寅月(2) → (2 + 0*2) % 10 = 2 → 丙 ✓
    offset = (reference_gan_index % 5) * 2
    month_stem_idx = (month_zhi_idx + offset) % 10
    month_gan = TIANGAN[month_stem_idx]

    return (month_gan, month_zhi)


def get_month_branch_by_date(date_obj):
    """
    根据公历日期获取月支。

    这是一个便捷函数，通过节气查找来确定月支。

    参数:
        date_obj: date 或 datetime 对象

    返回:
        (branch_name, branch_index): 地支名称(如"寅")和其索引(0-11)
    """
    from .solar_terms import (
        get_current_solar_term,
    )

    prev_term, prev_date, next_term, next_date = get_current_solar_term(date_obj)

    if prev_term in _SOLAR_TERM_TO_MONTH_BRANCH:
        return _SOLAR_TERM_TO_MONTH_BRANCH[prev_term]

    # prev_term 是"气", 回溯到最近的"节"
    year = date_obj.year
    from .solar_terms import get_all_solar_terms

    try:
        prev_year_terms = get_all_solar_terms(year - 1)
        all_terms = prev_year_terms + get_all_solar_terms(year)
    except Exception:
        all_terms = get_all_solar_terms(year)

    all_terms.sort(key=lambda x: x["date"])

    if isinstance(date_obj, datetime):
        target = date_obj
    else:
        target = datetime(date_obj.year, date_obj.month, date_obj.day)

    for t in reversed(all_terms):
        if t["name"] not in _SOLAR_TERM_TO_MONTH_BRANCH:
            continue
        t_date = t["date"]
        if isinstance(t_date, datetime):
            t_dt = t_date
        else:
            t_dt = datetime(t_date.year, t_date.month, t_date.day)
        if t_dt <= target:
            return _SOLAR_TERM_TO_MONTH_BRANCH[t["name"]]

    raise ValueError(f"无法确定日期 {date_obj} 的月支")


# ============================================================
# 时柱计算
# ============================================================

def get_hour_pillar(day_gan, hour):
    """
    根据日干和时辰计算时柱。

    日上起时法（五鼠遁）:
      甲己还加甲 → 甲子时开始
      乙庚丙作初 → 丙子时开始
      丙辛从戊起 → 戊子时开始
      丁壬庚子居 → 庚子时开始
      戊癸何方发 → 壬子开始
      壬子是真途

    天干计算公式:
      hour_stem_index = (hour_branch_index + day_stem_offset) % 10
      其中 day_stem_offset = (day_gan_index % 5) * 2

    参数:
        day_gan: str, 日天干，如 "甲", "乙", "丙" 等
        hour: int, 0-23, 出生时辰 (小时)

    返回:
        (天干, 地支): 如("甲","子") 表示甲子时

    示例:
        >>> get_hour_pillar("甲", 0)   # 甲日, 子时(23-1时)
        ("甲", "子")
        >>> get_hour_pillar("甲", 12)  # 甲日, 午时(11-13时)
        ("庚", "午")
        >>> get_hour_pillar("丙", 5)   # 丙日, 卯时(5-7时)
        ("辛", "卯")

    异常:
        ValueError: 天干无效 或 小时无效
    """
    if day_gan not in TIANGAN:
        raise ValueError(f"无效天干: {day_gan}, 有效值: {TIANGAN}")

    day_gan_index = _gan_index(day_gan)
    hour_branch_index = get_hour_branch_index(hour)
    hour_branch = get_hour_branch(hour)

    # 五鼠遁: 子时天干 = _WU_SHU_DUN_BASE[day_gan_index]
    # 时干 = (子时天干 + 时辰地支偏移) % 10
    # 子时天干索引 = (day_gan_index % 5) * 2
    zi_shi_gan_index = (day_gan_index % 5) * 2
    hour_stem_index = (zi_shi_gan_index + hour_branch_index) % 10
    hour_gan = TIANGAN[hour_stem_index]

    return (hour_gan, hour_branch)


def get_day_gan_by_hour_gan(hour_gan, hour_branch, target_day_gan_options):
    """
    根据时柱反推可能的日干。
    用于时辰已知但日干不确定时的推断场景。

    参数:
        hour_gan: str, 时天干
        hour_branch: str, 时地支
        target_day_gan_options: list of str, 候选日干

    返回:
        list of str: 符合时柱的日干
    """
    zi_shi_gan_index = _gan_index(hour_gan)
    hour_branch_index = _zhi_index(hour_branch)
    base_day_gan_mod = (zi_shi_gan_index - hour_branch_index) % 10

    # day_gan % 5 = base_day_gan_mod / 2
    # 因为 zi_shi_gan = (day_gan % 5) * 2
    # 所以 day_gan % 5 = zi_shi_gan / 2 (需要zi_shi_gan为偶数)
    if base_day_gan_mod % 2 != 0:
        return []  # 不可能的组合

    target_mod = base_day_gan_mod // 2

    result = []
    for gan in target_day_gan_options:
        if _gan_index(gan) % 5 == target_mod:
            result.append(gan)

    return result
