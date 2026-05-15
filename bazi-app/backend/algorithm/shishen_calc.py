"""
十神计算模块
============
根据日干与其他天干的关系，计算十神（比肩、劫财、食神、伤官、
偏财、正财、七杀、正官、偏印、正印）。
"""

from ._constants import (
    GAN, GAN_WUXING_LIST, GAN_YINYANG_LIST,
    WUXING_SHENG, WUXING_KE,
    WUXING_BEI_SHENG, WUXING_BEI_KE,
    SHISHEN_NAMES, PILLAR_NAMES,
)


def _gan_index(gan: str) -> int:
    """获取天干在 GAN 中的索引"""
    return GAN.index(gan)


def calculate_shishen(day_gan: str, other_gan: str) -> str:
    """
    计算单个天干与日干的十神关系。

    参数:
        day_gan: 日干（我）
        other_gan: 他干

    返回:
        十神名称字符串

    规则:
        - 同五行 + 同阴阳 → 比肩
        - 同五行 + 异阴阳 → 劫财
        - 我生 + 同阴阳 → 食神
        - 我生 + 异阴阳 → 伤官
        - 我克 + 同阴阳 → 偏财
        - 我克 + 异阴阳 → 正财
        - 克我 + 同阴阳 → 七杀
        - 克我 + 异阴阳 → 正官
        - 生我 + 同阴阳 → 偏印
        - 生我 + 异阴阳 → 正印
    """
    if day_gan == other_gan:
        return "比肩"

    dw = GAN_WUXING_LIST[_gan_index(day_gan)]   # 日干五行
    ow = GAN_WUXING_LIST[_gan_index(other_gan)]  # 他干五行
    dy = GAN_YINYANG_LIST[_gan_index(day_gan)]    # 日干阴阳
    oy = GAN_YINYANG_LIST[_gan_index(other_gan)]  # 他干阴阳

    same_yin_yang = (dy == oy)

    if dw == ow:
        # 同五行
        return "比肩" if same_yin_yang else "劫财"
    elif WUXING_SHENG.get(dw) == ow:
        # 我生
        return "食神" if same_yin_yang else "伤官"
    elif WUXING_KE.get(dw) == ow:
        # 我克
        return "偏财" if same_yin_yang else "正财"
    elif WUXING_KE.get(ow) == dw:
        # 克我
        return "七杀" if same_yin_yang else "正官"
    elif WUXING_SHENG.get(ow) == dw:
        # 生我
        return "偏印" if same_yin_yang else "正印"

    return "未知"


def get_all_shishen_mapping(day_gan: str) -> dict:
    """
    获取日干与所有十天干的十神映射表。

    参数:
        day_gan: 日干

    返回:
        {他干: 十神名称} 的字典
    """
    return {g: calculate_shishen(day_gan, g) for g in GAN}


def get_shishen_wuxing(shishen: str, day_gan: str) -> str:
    """
    根据十神名称反推对应的五行。

    参数:
        shishen: 十神名称
        day_gan: 日干

    返回:
        对应的五行字符串
    """
    dw = GAN_WUXING_LIST[_gan_index(day_gan)]

    mapping = {
        "比肩": dw,
        "劫财": dw,
        "食神": WUXING_SHENG[dw],
        "伤官": WUXING_SHENG[dw],
        "偏财": WUXING_KE[dw],
        "正财": WUXING_KE[dw],
        "七杀": WUXING_BEI_KE[dw],
        "正官": WUXING_BEI_KE[dw],
        "偏印": WUXING_BEI_SHENG[dw],
        "正印": WUXING_BEI_SHENG[dw],
    }
    return mapping.get(shishen, "未知")


def analyze_shishen_distribution(four_pillars: dict) -> dict:
    """
    分析十神在四柱中的分布情况。

    参数:
        four_pillars: 四柱数据，包含 year/month/day/hour 四个柱

    返回:
        {
            "distribution": {
                "年柱": {"天干十神": "正官", "地支藏干十神": [...]},
                "月柱": {...},
                "日柱": {...},  # 日柱天干为日主本人
                "时柱": {...},
            },
            "summary": {"比肩": 2, "劫财": 1, ...},
            "gan_summary": {"比肩": 1, ...},
            "zhi_summary": {"比肩": 1, ...},
        }
    """
    day_gan = four_pillars["day"]["gan"]
    labels = ["年柱", "月柱", "日柱", "时柱"]
    keys = ["year", "month", "day", "hour"]

    distribution = {}
    gan_summary = {name: 0 for name in SHISHEN_NAMES}
    zhi_summary = {name: 0 for name in SHISHEN_NAMES}

    for key, label in zip(keys, labels):
        pillar = four_pillars[key]
        gan = pillar["gan"]
        zhi = pillar["zhi"]
        canggan = pillar.get("canggan", [])

        # 天干十神
        gan_ss = calculate_shishen(day_gan, gan)
        if key != "day":
            gan_summary[gan_ss] = gan_summary.get(gan_ss, 0) + 1

        # 地支藏干十神
        zhi_ss_list = []
        for cg in canggan:
            cg_name = cg if isinstance(cg, str) else cg[0] if isinstance(cg, (tuple, list)) else cg
            ss = calculate_shishen(day_gan, cg_name)
            zhi_ss_list.append({"藏干": cg_name, "十神": ss})
            if key != "day":
                zhi_summary[ss] = zhi_summary.get(ss, 0) + 1

        distribution[label] = {
            "干支": pillar["ganzhi"],
            "天干": gan,
            "天干十神": gan_ss,
            "地支": zhi,
            "藏干十神": zhi_ss_list,
        }

    # 总体统计
    summary = {}
    for name in SHISHEN_NAMES:
        total = gan_summary.get(name, 0) + zhi_summary.get(name, 0)
        if total > 0:
            summary[name] = total

    return {
        "distribution": distribution,
        "summary": summary,
        "gan_summary": dict(gan_summary),
        "zhi_summary": dict(zhi_summary),
    }


def classify_shishen_groups(summary: dict) -> dict:
    """
    将十神分为吉神、凶神、中性三类。

    吉神: 正印, 食神, 正官, 正财, 比肩
    凶神: 七杀, 伤官, 劫财, 偏印, 偏财 (偏财在特定情况下也可为吉)
    """
    ji_shen = {"正印", "食神", "正官", "正财", "比肩"}
    xiong_shen = {"七杀", "伤官", "劫财", "偏印", "偏财"}

    result = {"吉神": {}, "凶神": {}}
    for name, count in summary.items():
        if name in ji_shen:
            result["吉神"][name] = count
        elif name in xiong_shen:
            result["凶神"][name] = count

    return result
