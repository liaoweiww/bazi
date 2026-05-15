"""
大运与流年推算
==============
根据八字命盘和性别推算大运 (十年一运) 和流年运势。

大运规则:
1. 阳年男/阴年女 → 顺排 (月柱往后排)
   阴年男/阳年女 → 逆排 (月柱往前排)
2. 起运岁数: 从出生日到下一个节气 (顺排) 或上一个节气 (逆排) 的天数 ÷ 3
3. 每 10 年一步大运

流年规则:
- 每年干支按公式: 年干 = (year-4)%10, 年支 = (year-4)%12
- 流年与四柱的刑冲合害关系分析
"""

from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

from ._constants import (
    GAN, GAN_WUXING_LIST, GAN_YINYANG_LIST,
    ZHI, ZHI_WUXING_LIST,
    NAYIN_DATA,
    JIE_INDICES, JIE_ZHI,
    ZHI_LIUCHONG, ZHI_LIUHE, ZHI_LIUHAI,
    ZHI_SANHE, ZHI_SANXING, ZHI_ZIXING,
    SHICHEN_MAP,
)

from .shishen_calc import calculate_shishen


def _gan_index(gan: str) -> int:
    return GAN.index(gan)


def _zhi_index(zhi: str) -> int:
    return ZHI.index(zhi)


def _get_nayin(gan: str, zhi: str) -> Tuple[str, str]:
    """获取纳音"""
    g_idx = _gan_index(gan)
    z_idx = _zhi_index(zhi)
    k = (5 * (z_idx - g_idx) // 2) % 6
    n = (g_idx + 10 * k) % 60
    return NAYIN_DATA[n // 2]


# =============================================================================
# 大运推算
# =============================================================================

def calculate_dayun(four_pillars: dict, gender: str, birth_date) -> Dict:
    """
    推算大运。

    参数:
        four_pillars: 四柱数据 (含 year_gan, month_gan, month_zhi 等)
        gender: 性别 ("男" 或 "女")
        birth_date: 出生日期 (date 对象 或 (year, month, day)元组)

    返回:
        {
            "start_age": 8,
            "direction": "顺排" / "逆排",
            "dayun_list": [
                {"age_range": "8-17", "ganzhi": "癸未", ...},
                ...
            ],
        }
    """
    year_gan = four_pillars["year"]["gan"]
    month_gan = four_pillars["month"]["gan"]
    month_zhi = four_pillars["month"]["zhi"]

    # 判断顺逆
    is_yang = GAN_YINYANG_LIST[_gan_index(year_gan)] == "阳"
    if (is_yang and gender == "男") or (not is_yang and gender == "女"):
        direction = "顺排"
    else:
        direction = "逆排"

    # 解析出生日期
    if isinstance(birth_date, (list, tuple)):
        by, bm, bd = birth_date[0], birth_date[1], birth_date[2]
        bdate = date(by, bm, bd)
    elif isinstance(birth_date, date):
        bdate = birth_date
    elif isinstance(birth_date, str):
        parts = birth_date.split("-")
        bdate = date(int(parts[0]), int(parts[1]), int(parts[2]))
    else:
        bdate = birth_date

    # 计算起运岁数: 距离上/下一个"节"的天数 ÷ 3
    start_age = _calc_start_age(bdate, direction)

    # 排列大运 (共 8 步)
    dayun_list = _build_dayun_sequence(month_gan, month_zhi, direction, start_age)

    return {
        "start_age": start_age,
        "direction": direction,
        "dayun_list": dayun_list,
    }


def _calc_start_age(birth_date: date, direction: str) -> float:
    """
    计算起运岁数。

    顺排: 到下一个"节"的天数 / 3
    逆排: 到上一个"节"的天数 / 3

    返回:
        起运岁数 (精确到1位小数)
    """
    # 获取所有相关年份的节气日期
    # 需要使用节气计算
    from .paipan import _get_solar_term_date

    year = birth_date.year

    # 收集所有 12 个节在该年前后的日期
    jie_dates = []
    for month_idx, term_idx in enumerate(JIE_INDICES):
        # 跨年处理: 大雪和冬至在前一年12月, 小寒在当年1月
        for y_offset in [-1, 0, 1]:
            try:
                sy, sm, sd = _get_solar_term_date(year + y_offset, term_idx)
                jie_dates.append((month_idx, date(sy, sm, sd)))
            except Exception:
                pass

    # 去重并按日期排序
    seen = set()
    unique_jies = []
    for mi, d in sorted(jie_dates, key=lambda x: x[1]):
        if d not in seen:
            seen.add(d)
            unique_jies.append((mi, d))

    if direction == "顺排":
        # 找第一个在出生日期之后的节
        for _, d in unique_jies:
            if d > birth_date:
                days_diff = (d - birth_date).days
                return round(days_diff / 3.0, 1)
        # 如果没找到，用下一年第一个节
        for y in range(year + 1, year + 3):
            for month_idx, term_idx in enumerate(JIE_INDICES):
                sy, sm, sd = _get_solar_term_date(y, term_idx)
                d = date(sy, sm, sd)
                if d > birth_date:
                    return round((d - birth_date).days / 3.0, 1)
        return 1.0
    else:
        # 逆排: 找最后一个在出生日期之前的节
        prev_jie = None
        for _, d in unique_jies:
            if d < birth_date:
                prev_jie = d
            else:
                break
        if prev_jie:
            days_diff = (birth_date - prev_jie).days
            return round(days_diff / 3.0, 1)
        # 如果没找到，用上一年最后一个节
        for y in range(year - 1, year - 3, -1):
            for month_idx in range(11, -1, -1):
                term_idx = JIE_INDICES[month_idx]
                sy, sm, sd = _get_solar_term_date(y, term_idx)
                d = date(sy, sm, sd)
                if d < birth_date:
                    return round((birth_date - d).days / 3.0, 1)
        return 1.0


def _build_dayun_sequence(month_gan: str, month_zhi: str,
                           direction: str, start_age: float) -> List[Dict]:
    """
    从月柱出发，按顺/逆方向排 8 步大运。

    返回:
        [{"age_range": "8-17", "ganzhi": "癸未", "gan": "癸", "zhi": "未", "nayin": "..."}, ...]
    """
    gan_idx = _gan_index(month_gan)
    zhi_idx = _zhi_index(month_zhi)
    step = 1 if direction == "顺排" else -1

    dayun_list = []
    for i in range(1, 9):
        new_gan = GAN[(gan_idx + step * i) % 10]
        new_zhi = ZHI[(zhi_idx + step * i) % 12]
        ganzhi = new_gan + new_zhi
        nayin_name, nayin_wx = _get_nayin(new_gan, new_zhi)

        start = int(start_age + (i - 1) * 10)
        end = int(start_age + i * 10 - 1)

        dayun_list.append({
            "step": i,
            "age_range": f"{start}-{end}",
            "start_age": start_age + (i - 1) * 10,
            "gan": new_gan,
            "zhi": new_zhi,
            "ganzhi": ganzhi,
            "gan_wuxing": GAN_WUXING_LIST[_gan_index(new_gan)],
            "zhi_wuxing": ZHI_WUXING_LIST[_zhi_index(new_zhi)],
            "nayin": nayin_name,
            "nayin_wuxing": nayin_wx,
        })

    return dayun_list


# =============================================================================
# 流年推算
# =============================================================================

def calculate_liunian(four_pillars: dict, year: int) -> Dict:
    """
    推算特定年份的流年运势。

    参数:
        four_pillars: 四柱数据
        year: 目标年份 (如 2026)

    返回:
        {
            "ganzhi": "丙午",
            "gan": "丙", "zhi": "午",
            "wuxing": "火",
            "shishen": "偏印",
            "nayin": "天河水",
            "relations": {
                "with_day_zhi": "无特殊关系",
                "with_year_zhi": "六冲",
                ...
            },
            "analysis": "流年丙午，..."
        }
    """
    day_gan = four_pillars["day"]["gan"]

    # 流年干支
    year_gan = GAN[(year - 4) % 10]
    year_zhi = ZHI[(year - 4) % 12]
    liunian_ganzhi = year_gan + year_zhi

    # 流年十神
    shishen = calculate_shishen(day_gan, year_gan)
    year_wx = GAN_WUXING_LIST[_gan_index(year_gan)]

    # 流年与四柱地支的关系
    relations = {}
    for pkey in ["year", "month", "day", "hour"]:
        pzhi = four_pillars[pkey]["zhi"]
        rel = _check_zhi_relation(year_zhi, pzhi)
        if rel:
            relations[f"with_{pkey}_zhi"] = rel

    # 纳音
    nayin_name, nayin_wx = _get_nayin(year_gan, year_zhi)

    # 分析文本
    analysis = _build_liunian_analysis(liunian_ganzhi, shishen, relations)

    return {
        "year": year,
        "ganzhi": liunian_ganzhi,
        "gan": year_gan,
        "zhi": year_zhi,
        "wuxing": year_wx,
        "shishen": shishen,
        "nayin": nayin_name,
        "nayin_wuxing": nayin_wx,
        "relations": relations,
        "analysis": analysis,
    }


def _check_zhi_relation(zhi1: str, zhi2: str) -> Optional[str]:
    """
    检查两地支之间的特殊关系。

    返回:
        关系描述字符串 (六冲/六合/六害/三刑/伏吟等) 或 None
    """
    if zhi1 == zhi2:
        return "伏吟 (相同地支)"

    # 六冲
    if ZHI_LIUCHONG.get(zhi1) == zhi2:
        return f"六冲 ({zhi1}冲{zhi2})"

    # 六合
    he_wx = ZHI_LIUHE.get((zhi1, zhi2), "")
    if he_wx:
        return f"六合 ({zhi1}合{zhi2}化{he_wx})"

    # 六害
    if ZHI_LIUHAI.get(zhi1) == zhi2:
        return f"六害 ({zhi1}害{zhi2})"

    # 三合
    for tri_set, wx in ZHI_SANHE:
        if zhi1 in tri_set and zhi2 in tri_set and zhi1 != zhi2:
            return f"三合 ({zhi1}{zhi2}半合{wx}局)"

    # 三刑
    xing = ZHI_SANXING.get(zhi1, "")
    if xing == zhi2:
        return f"相刑 ({zhi1}刑{zhi2})"

    return None


def _build_liunian_analysis(ganzhi: str, shishen: str,
                             relations: dict) -> str:
    """
    构建流年分析文本。
    """
    parts = [f"流年{ganzhi}，天干为{shishen}"]

    for rel_key, rel_desc in relations.items():
        pillar_name = rel_key.replace("with_", "").replace("_zhi", "柱")
        parts.append(f"与{pillar_name}{rel_desc}")

    if len(relations) >= 2:
        parts.append("该年变动较多，宜谨慎行事。")
    elif len(relations) == 0:
        parts.append("该年较为平稳。")

    return "，".join(parts)


# =============================================================================
# 综合运势函数
# =============================================================================

def get_current_dayun(dayun_result: dict, current_age: float) -> Optional[Dict]:
    """
    根据当前年龄获取所处的大运。

    参数:
        dayun_result: calculate_dayun 的返回结果
        current_age: 当前年龄

    返回:
        所处大运的条目，或 None
    """
    for dy in dayun_result.get("dayun_list", []):
        start = dy["start_age"]
        if start <= current_age < start + 10:
            return dy
    return None


def get_liunian_multi_year(four_pillars: dict,
                            start_year: int,
                            end_year: int) -> List[Dict]:
    """
    批量推算多年流年。

    返回:
        [流年结果列表]
    """
    results = []
    for yr in range(start_year, end_year + 1):
        results.append(calculate_liunian(four_pillars, yr))
    return results
