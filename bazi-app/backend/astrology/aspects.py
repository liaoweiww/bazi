"""
相位计算模块
============
计算行星间的5种主要相位（合/六分/四分/三分/对分）。
"""

from .constants import ASPECT_TYPES


def calc_aspects(planets, orb_factor=1.0):
    """
    计算所有行星对之间的相位。

    参数:
        planets: [{name_cn, lon, ...}, ...] 行星列表，需包含 'lon' 键
        orb_factor: 容许度系数 (默认1.0)

    返回:
        [{planet1, planet2, aspect_type, angle_diff, orb, nature}, ...]
        按相位重要性排序 (合相优先，然后角度小的)
    """
    aspects = []
    n = len(planets)

    for i in range(n):
        for j in range(i + 1, n):
            lon1 = planets[i]["lon"]
            lon2 = planets[j]["lon"]
            diff = abs(lon1 - lon2)
            if diff > 180:
                diff = 360 - diff

            for asp in ASPECT_TYPES:
                effective_orb = asp["orb"] * orb_factor
                angle_diff = abs(diff - asp["angle"])
                if angle_diff <= effective_orb:
                    aspects.append({
                        "planet1": planets[i]["name_cn"],
                        "planet2": planets[j]["name_cn"],
                        "planet1_lon": round(lon1, 2),
                        "planet2_lon": round(lon2, 2),
                        "aspect_name_cn": asp["name_cn"],
                        "aspect_name_en": asp["name_en"],
                        "aspect_symbol": asp["symbol"],
                        "angle": diff,
                        "angle_diff": round(angle_diff, 2),
                        "orb": round(effective_orb, 2),
                        "nature": asp["nature"],
                        "keyword": asp["keyword"],
                    })
                    break  # 每个行星对只取一种相位

    # 按重要性排序：合相 > 对分相 > 四分相 > 三分相 > 六分相
    priority = {"合相": 1, "对分相": 2, "四分相": 3, "三分相": 4, "六分相": 5}
    aspects.sort(key=lambda a: (priority.get(a["aspect_name_cn"], 10), abs(a["angle_diff"])))

    return aspects


def detect_aspect_patterns(aspects, planets):
    """
    检测特殊的相位格局。

    返回:
        [pattern_name_cn, ...]
    """
    patterns = []

    # 构建非正式的行星对集合
    aspect_pairs = set()
    for a in aspects:
        pair = (a["planet1"], a["planet2"])
        aspect_pairs.add(pair)

    # 检测主要格局
    # T三角: 两颗行星对分，分别与第三颗行星四分
    oppositions = [a for a in aspects if a["aspect_name_cn"] == "对分相"]
    squares = [a for a in aspects if a["aspect_name_cn"] == "四分相"]

    for opp in oppositions:
        p1, p2 = opp["planet1"], opp["planet2"]
        for sq in squares:
            if sq["planet1"] in (p1, p2) and sq["planet2"] not in (p1, p2):
                if "T三角 (T-Square)" not in patterns:
                    # 验证第三个行星也参与四分相
                    for sq2 in squares:
                        if sq2["planet1"] == sq["planet2"] and sq2["planet2"] in (p1, p2):
                            patterns.append("T三角 (T-Square)")
                            break

    # 大三角: 三颗行星两两间均为三分相
    trines = [a for a in aspects if a["aspect_name_cn"] == "三分相"]
    trine_pairs = []
    for t in trines:
        trine_pairs.append((t["planet1"], t["planet2"]))

    if len(trines) >= 3:
        # 统计每个行星参与的三分相数量
        from collections import Counter
        planet_counts = Counter()
        for p1, p2 in trine_pairs:
            planet_counts[p1] += 1
            planet_counts[p2] += 1

        # 寻找度 ≥ 2 的行星组
        grand_trine_planets = [p for p, c in planet_counts.items() if c >= 2]
        if len(grand_trine_planets) >= 3:
            patterns.append("大三角 (Grand Trine)")

    # 大十字: 四颗以上行星构成两个对分+两组四分
    if len(oppositions) >= 2 and len(squares) >= 4:
        patterns.append("大十字 (Grand Cross)")

    # 风筝: 大三角 + 一组对分
    if "大三角 (Grand Trine)" in patterns and len(oppositions) >= 1:
        patterns.append("风筝 (Kite)")

    return patterns
