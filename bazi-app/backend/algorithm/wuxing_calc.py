"""
五行量化与身强身弱判定
======================
统计八字中五行分布数量与分值，并综合月令、通根、
生助三方面判断日主身强身弱。
"""

from ._constants import (
    GAN, GAN_WUXING, GAN_YINYANG, GAN_WUXING_LIST, GAN_YINYANG_LIST,
    ZHI, ZHI_WUXING, ZHI_WUXING_LIST, ZHI_YINYANG_LIST,
    CANG_GAN,
    WUXING_SHENG, WUXING_KE,
    WUXING_BEI_SHENG, WUXING_BEI_KE,
    MONTH_ZHI_WUXING,
)


def _gan_index(gan: str) -> int:
    return GAN.index(gan)


def _zhi_index(zhi: str) -> int:
    return ZHI.index(zhi)


def count_wuxing(four_pillars: dict) -> dict:
    """
    统计八字中五行数量与分值。

    计分规则:
    - 天干每字: 1 分
    - 地支本气: 1 分
    - 地支中气/余气: 各 0.5 分

    参数:
        four_pillars: 四柱数据 (来自 paipan 的 four_pillars)

    返回:
        {
            "木": {"count": 3.0, "score": 3.0},
            "火": {"count": 2.5, "score": 2.5},
            ...
        }
    """
    wuxing_count = {
        "金": {"count": 0.0, "score": 0.0, "details": []},
        "木": {"count": 0.0, "score": 0.0, "details": []},
        "水": {"count": 0.0, "score": 0.0, "details": []},
        "火": {"count": 0.0, "score": 0.0, "details": []},
        "土": {"count": 0.0, "score": 0.0, "details": []},
    }

    pillar_names = {"year": "年柱", "month": "月柱", "day": "日柱", "hour": "时柱"}

    for pkey, pillar in four_pillars.items():
        pname = pillar_names.get(pkey, pkey)

        # 天干
        gan = pillar.get("gan", "")
        wx = GAN_WUXING.get(gan, "")
        if wx:
            wuxing_count[wx]["count"] += 1.0
            wuxing_count[wx]["score"] += 1.0
            wuxing_count[wx]["details"].append(f"{pname}天干{gan}({wx})+1")

        # 地支藏干
        canggan = pillar.get("canggan", [])
        if isinstance(canggan, list):
            for i, cg in enumerate(canggan):
                cg_name = cg if isinstance(cg, str) else cg[0] if isinstance(cg, (tuple, list)) else str(cg)
                cg_wx = GAN_WUXING.get(cg_name, "")
                if cg_wx:
                    if i == 0:  # 本气
                        weight = 1.0
                        label = "本气"
                    else:  # 余气/中气
                        weight = 0.5
                        label = "余气"
                    wuxing_count[cg_wx]["count"] += 1.0 if weight == 1.0 else 0.5
                    wuxing_count[cg_wx]["score"] += weight
                    wz = pillar.get("zhi", "?")
                    wuxing_count[cg_wx]["details"].append(
                        f"{pname}地支{wz}({cg_name}/{cg_wx})+{weight}")

    # 四舍五入到一位小数
    for wx in wuxing_count:
        wuxing_count[wx]["score"] = round(wuxing_count[wx]["score"], 1)
        wuxing_count[wx]["count"] = round(wuxing_count[wx]["count"], 1)

    return wuxing_count


def check_deling(four_pillars: dict, day_master: str) -> bool:
    """
    判断「得令」: 日主五行是否与月令 (月支) 五行相同。

    月令为八字中最重要的一柱，得令者日主得时令之助。

    参数:
        four_pillars: 四柱数据
        day_master: 日干 (如 "戊")

    返回:
        True 如果得令, False 否则
    """
    dm_wx = GAN_WUXING_LIST[_gan_index(day_master)]
    month_zhi = four_pillars["month"]["zhi"]
    month_wx = ZHI_WUXING_LIST[_zhi_index(month_zhi)]

    return dm_wx == month_wx


def check_dedi(four_pillars: dict, day_master: str) -> bool:
    """
    判断「得地」: 日干在地支是否有通根 (藏干包含日主五行)。

    参数:
        four_pillars: 四柱数据
        day_master: 日干

    返回:
        True 如果得地, False 否则
    """
    dm_wx = GAN_WUXING_LIST[_gan_index(day_master)]

    for pkey in ["year", "month", "day", "hour"]:
        pillar = four_pillars.get(pkey, {})
        canggan_raw = pillar.get("canggan", [])
        if isinstance(canggan_raw, list):
            for cg in canggan_raw:
                cg_name = cg if isinstance(cg, str) else cg[0] if isinstance(cg, (tuple, list)) else str(cg)
                if GAN_WUXING.get(cg_name) == dm_wx:
                    return True
    return False


def check_deshi(four_pillars: dict, day_master: str) -> bool:
    """
    判断「得势」: 四柱中生日主的五行 (印星) 和其他比劫是否足够多。

    得势的标准: 除日主外，至少有 2 柱天干为印星或比劫 (生扶日主)。

    参数:
        four_pillars: 四柱数据
        day_master: 日干

    返回:
        True 如果得势, False 否则
    """
    dm_wx = GAN_WUXING_LIST[_gan_index(day_master)]

    # 印星五行 = 生日主的五行
    yin_wx = WUXING_BEI_SHENG.get(dm_wx, "")  # 生我者

    support_count = 0
    for pkey in ["year", "month", "hour"]:  # 排除日柱自身
        pillar = four_pillars.get(pkey, {})
        gan = pillar.get("gan", "")
        gan_wx = GAN_WUXING.get(gan, "")
        if gan_wx == dm_wx or gan_wx == yin_wx:
            support_count += 1

    return support_count >= 2


def determine_strength(four_pillars: dict) -> dict:
    """
    身强身弱综合判定 (核心算法)。

    采用三方面加权评分:
    1. 月令 (50% 权重) - 最重要
       - 得令: 日主五行与月支五行相同 → +25 分
       - 月令生日主 (印星当令) → +15 分
       - 日主生月令 (食伤当令) → -15 分
       - 月令克日主 (官杀当令) → -25 分
    2. 通根 (30% 权重)
       - 地支有多处藏干同五行 → +15 分
       - 有 1 处通根 → +8 分
       - 无通根 → -10 分
    3. 生助 (20% 权重)
       - 天干印星+比劫多 → +10 分
       - 略有生助 → +3 分
       - 少生助 → -5 分

    综合评分判定:
    - score >= 70: 身强
    - 55 <= score < 70: 偏强
    - 45 <= score < 55: 中和
    - 30 <= score < 45: 偏弱
    - score < 30: 身弱

    参数:
        four_pillars: 四柱数据

    返回:
        {
            "level": "身强" / "偏强" / "中和" / "偏弱" / "身弱",
            "score": 75,
            "deling": True,
            "dedi": True,
            "deshi": False,
            "details": "..."
        }
    """
    day_gan = four_pillars["day"]["gan"]
    dm_wx = GAN_WUXING_LIST[_gan_index(day_gan)]
    month_zhi = four_pillars["month"]["zhi"]
    month_wx = ZHI_WUXING_LIST[_zhi_index(month_zhi)]

    score = 50.0  # 基准分
    detail_parts = []

    # ---- 1. 得令判断 (50% 权重) ----
    deling = False
    if dm_wx == month_wx:
        score += 25
        deling = True
        detail_parts.append(f"日主{dm_wx}与月令{month_zhi}({month_wx})同五行，得令 (+25)")
    elif WUXING_BEI_SHENG.get(dm_wx) == month_wx:
        # 月令生日主 (印星月)
        score += 15
        detail_parts.append(f"月令{month_zhi}({month_wx})生日主{dm_wx}，印星当令 (+15)")
    elif WUXING_SHENG.get(dm_wx) == month_wx:
        # 日主生月令 (食伤泄气)
        score -= 15
        detail_parts.append(f"日主{dm_wx}生月令{month_zhi}({month_wx})，食伤泄气 (-15)")
    elif WUXING_KE.get(month_wx) == dm_wx:
        # 月令克日主 (官杀当令)
        score -= 25
        detail_parts.append(f"月令{month_zhi}({month_wx})克日主{dm_wx}，官杀当令 (-25)")
    else:
        detail_parts.append(f"日主{dm_wx}与月令{month_zhi}({month_wx})关系一般")

    # ---- 2. 通根判断 (30% 权重) ----
    dedi = check_dedi(four_pillars, day_gan)

    # 统计所有藏干中日主同五行的数量
    root_count = 0
    root_details = []
    for pkey in ["year", "month", "day", "hour"]:
        pillar = four_pillars.get(pkey, {})
        zhi = pillar.get("zhi", "")
        canggan_raw = pillar.get("canggan", [])
        if isinstance(canggan_raw, list):
            for cg in canggan_raw:
                cg_name = cg if isinstance(cg, str) else cg[0] if isinstance(cg, (tuple, list)) else str(cg)
                if GAN_WUXING.get(cg_name) == dm_wx:
                    root_count += 1
                    root_details.append(f"{zhi}藏{cg_name}({dm_wx})")

    if root_count >= 3:
        score += 15
        detail_parts.append(f"地支多处通根({', '.join(root_details)})，得地深厚 (+15)")
    elif root_count >= 2:
        score += 10
        detail_parts.append(f"地支有{root_count}处通根({', '.join(root_details)})，得地 (+10)")
    elif root_count >= 1:
        score += 5
        detail_parts.append(f"地支{root_count}处通根({', '.join(root_details)})，略有根气 (+5)")
    else:
        score -= 10
        detail_parts.append("地支无通根，失地 (-10)")

    # ---- 3. 生助判断 (20% 权重) ----
    deshi = check_deshi(four_pillars, day_gan)
    yin_wx = WUXING_BEI_SHENG.get(dm_wx, "")

    support_count = 0
    support_details = []
    for pkey in ["year", "month", "hour"]:
        pillar = four_pillars.get(pkey, {})
        gan = pillar.get("gan", "")
        gan_wx = GAN_WUXING.get(gan, "")
        if gan_wx == dm_wx:
            support_count += 1
            support_details.append(f"{pkey}干{gan}(比劫)")
        elif gan_wx == yin_wx:
            support_count += 1
            support_details.append(f"{pkey}干{gan}(印星)")

    if support_count >= 3:
        score += 10
        detail_parts.append(f"天干生助多({', '.join(support_details)})，得势 (+10)")
    elif support_count >= 2:
        score += 5
        detail_parts.append(f"天干有{', '.join(support_details)}，略有得势 (+5)")
    elif support_count >= 1:
        score += 2
        detail_parts.append(f"天干{', '.join(support_details)}，势单 (+2)")
    else:
        score -= 5
        detail_parts.append("天干少生助，失势 (-5)")

    # ---- 综合判定 ----
    if score >= 70:
        level = "身强"
    elif score >= 55:
        level = "偏强"
    elif score >= 45:
        level = "中和"
    elif score >= 30:
        level = "偏弱"
    else:
        level = "身弱"

    return {
        "level": level,
        "score": round(score, 1),
        "deling": deling,
        "dedi": dedi,
        "deshi": deshi,
        "details": "；".join(detail_parts),
    }
