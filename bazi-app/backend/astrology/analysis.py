"""
星盘分析模块
============
元素分布、模式分布、半球分析、格局识别。
"""

from .constants import ELEMENTS, MODALITIES


def analyze_chart(planets):
    """
    分析星盘的整体特征。

    参数:
        planets: [{name_cn, sign, sign_element, sign_modality, lon, house, ...}, ...]

    返回:
        {
            "elements": {火: {count, percentage, planets, assessment}, ...},
            "modalities": {基本: {count, percentage, ...}, ...},
            "dominant_element": str,
            "dominant_modality": str,
            "hemisphere": {above_horizon: ..., below_horizon: ..., east: ..., west: ...},
            "summary": str,
        }
    """
    # 只统计10颗主行星
    main_planets = [p for p in planets if p["name_cn"] in {
        "太阳", "月亮", "水星", "金星", "火星",
        "木星", "土星", "天王星", "海王星", "冥王星"
    }]

    total = len(main_planets) or 1

    # === 元素统计 ===
    element_counts = {"火": 0, "土": 0, "风": 0, "水": 0}
    element_planets = {"火": [], "土": [], "风": [], "水": []}
    for p in main_planets:
        el = p.get("sign_element", "")
        if el in element_counts:
            element_counts[el] += 1
            element_planets[el].append(p["name_cn"])

    elements_result = {}
    for el_name, el_info in ELEMENTS.items():
        count = element_counts[el_name]
        pct = round(count / total * 100, 1)
        elements_result[el_name] = {
            "count": count,
            "percentage": pct,
            "planets": element_planets[el_name],
            "name_cn": el_info["name_cn"],
            "traits": el_info["traits"],
        }
        # 解读
        if pct >= 50:
            elements_result[el_name]["assessment"] = f"{el_info['name_cn']}元素突出，{el_info['traits']}特质明显。"
        elif pct >= 30:
            elements_result[el_name]["assessment"] = f"{el_info['name_cn']}元素较强，具备一定的{el_info['traits']}。"
        elif pct >= 10:
            elements_result[el_name]["assessment"] = f"{el_info['name_cn']}元素适中。"
        elif pct == 0:
            elements_result[el_name]["assessment"] = f"{el_info['name_cn']}元素缺失，可能需要有意识地培养这方面的特质。"
        else:
            elements_result[el_name]["assessment"] = f"{el_info['name_cn']}元素较弱。"

    dominant_element = max(element_counts, key=element_counts.get)
    if element_counts[dominant_element] == 0:
        dominant_element = "火"

    # === 模式统计 ===
    modality_counts = {"基本": 0, "固定": 0, "变动": 0}
    modality_planets = {"基本": [], "固定": [], "变动": []}
    for p in main_planets:
        mod = p.get("sign_modality", "")
        if mod in modality_counts:
            modality_counts[mod] += 1
            modality_planets[mod].append(p["name_cn"])

    modalities_result = {}
    for mod_name, mod_info in MODALITIES.items():
        count = modality_counts[mod_name]
        pct = round(count / total * 100, 1)
        modalities_result[mod_name] = {
            "count": count,
            "percentage": pct,
            "planets": modality_planets[mod_name],
            "name_cn": mod_info["name_cn"],
            "traits": mod_info["traits"],
        }

    dominant_modality = max(modality_counts, key=modality_counts.get)

    # === 半球分析 ===
    # 上半球 (第7-12宫) vs 下半球 (第1-6宫)
    above = sum(1 for p in main_planets if p.get("house") and p["house"] >= 7 and p["house"] <= 12)
    below = sum(1 for p in main_planets if p.get("house") and p["house"] >= 1 and p["house"] <= 6)

    hemispheres = {
        "above_horizon": {"count": above, "meaning": "行星集中在上半球，人生重心偏向外界、社会成就、公共生活。"},
        "below_horizon": {"count": below, "meaning": "行星集中在下半球，人生重心偏向内在、家庭、个人成长。"},
    }

    # 东半球 (10-3) vs 西半球 (4-9)
    east = sum(1 for p in main_planets if p.get("house") and (p["house"] >= 10 or p["house"] <= 3))
    west = sum(1 for p in main_planets if p.get("house") and (p["house"] >= 4 and p["house"] <= 9))

    hemispheres["east"] = {"count": east, "meaning": "行星集中在东方(自我主导)，人生偏重主动开拓、自我表达。"}
    hemispheres["west"] = {"count": west, "meaning": "行星集中在西方(他人导向)，人生偏重合作关系、回应外界。"}

    # === 综览总结 ===
    el_desc = ELEMENTS[dominant_element]["name_cn"]
    mod_desc = MODALITIES[dominant_modality]["name_cn"]
    missing_elements = [el for el, c in element_counts.items() if c == 0]

    summary = f"你的星盘元素以{el_desc}为主导，模式以{mod_desc}为主。"
    if missing_elements:
        summary += f"缺乏{','.join(missing_elements)}元素，"
        summary += "可以通过后天学习来弥补这部分特质。"

    return {
        "elements": elements_result,
        "modalities": modalities_result,
        "dominant_element": dominant_element,
        "dominant_modality": dominant_modality,
        "hemispheres": hemispheres,
        "summary": summary,
    }
