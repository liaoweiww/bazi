"""
格局判定模块
============
判定八字格局类型，包括正格 (八格)、变格 (从格) 和专旺格。

格局判定规则:
- 正格: 以月令主气透出天干取格，分为八格
- 变格: 日主极旺或极弱时的特殊格局
- 专旺格: 五行一方之气独旺
"""

from ._constants import (
    GAN, GAN_WUXING, GAN_YINYANG, GAN_WUXING_LIST, GAN_YINYANG_LIST,
    ZHI, ZHI_WUXING, ZHI_WUXING_LIST,
    CANG_GAN,
    WUXING_SHENG, WUXING_KE,
    WUXING_BEI_SHENG, WUXING_BEI_KE,
    SEASON_ZHI,
)

from .shishen_calc import calculate_shishen


def _gan_index(gan: str) -> int:
    return GAN.index(gan)


def _zhi_index(zhi: str) -> int:
    return ZHI.index(zhi)


def _get_month_benqi(month_zhi: str) -> str:
    """获取月支本气天干"""
    cg = CANG_GAN.get(month_zhi, [])
    if cg:
        return cg[0][0]  # 第一个即本气
    return ""


def _count_wuxing_in_pillars(four_pillars: dict) -> dict:
    """
    统计四柱中每个五行的出现次数 (含天干和藏干)。

    返回:
        {五行: 出现次数}
    """
    counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}

    for pkey, pillar in four_pillars.items():
        # 天干
        gan = pillar.get("gan", "")
        wx = GAN_WUXING.get(gan, "")
        if wx:
            counts[wx] += 1

        # 藏干
        canggan = pillar.get("canggan", [])
        if isinstance(canggan, list):
            for cg in canggan:
                cg_name = cg if isinstance(cg, str) else cg[0] if isinstance(cg, (tuple, list)) else str(cg)
                cg_wx = GAN_WUXING.get(cg_name, "")
                if cg_wx:
                    counts[cg_wx] += 1

    return counts


# =============================================================================
# 正格判定 (八格)
# =============================================================================

def _determine_zhengge(four_pillars: dict) -> dict:
    """
    判定正格 (八格)。

    规则:
    1. 优先取月令本气透出天干为格
    2. 月令本气未透，看月令中气/余气是否透出
    3. 取月干或时干透出者为格
    4. 月令为子午卯酉: 只取本气
    5. 月令为寅申巳亥: 本气优先，中气可参
    6. 月令为辰戌丑未: 看透出何干

    返回:
        {"type": "正格", "name": "正官格", "analysis": "..."}
    """
    day_gan = four_pillars["day"]["gan"]
    month_zhi = four_pillars["month"]["zhi"]
    month_gan = four_pillars["month"]["gan"]

    # 月支藏干
    canggan_list = CANG_GAN.get(month_zhi, [])

    # 月令本气
    benqi = canggan_list[0][0] if canggan_list else ""

    # 查看月令的哪些藏干透出了天干 (在四柱天干中出现)
    all_gans = set()
    for pkey in four_pillars:
        all_gans.add(four_pillars[pkey]["gan"])

    # 筛选透出的藏干
    transparent_cg = []
    for cg, cg_type in canggan_list:
        if cg in all_gans:
            transparent_cg.append((cg, cg_type))

    # 确定取格
    ge_name = ""
    analysis_parts = [f"月令{month_zhi}"]

    if transparent_cg:
        # 有透出：取优先透出的本气
        chosen_cg = transparent_cg[0][0]
        shishen = calculate_shishen(day_gan, chosen_cg)
        ge_name = f"{shishen}格"
        analysis_parts.append(f"藏干{chosen_cg}透出天干")
        analysis_parts.append(f"取{ge_name}")
    else:
        # 没有藏干透出：取月干或月支本气
        # 优先看月干
        if month_gan:
            shishen = calculate_shishen(day_gan, month_gan)
            ge_name = f"{shishen}格"
            analysis_parts.append(f"月干{month_gan}为{shishen}，取{ge_name}")
        elif benqi:
            shishen = calculate_shishen(day_gan, benqi)
            ge_name = f"{shishen}格"
            analysis_parts.append(f"月支本气{benqi}为{shishen}，取{ge_name}")

    # 描述
    analysis = "，".join(analysis_parts) + "。"

    return {
        "type": "正格",
        "name": ge_name or f"杂气{month_zhi}月",
        "month_benqi": benqi,
        "transparent_gans": [cg for cg, _ in transparent_cg],
        "analysis": analysis,
    }


# =============================================================================
# 专旺格判定
# =============================================================================

def _check_zhuanwang(four_pillars: dict) -> dict:
    """
    判定专旺格。

    条件: 日主一方五行极旺，全盘几乎全是同一五行 (或其印星)。

    五种专旺格:
    - 曲直格 (木): 木旺于春 (寅卯辰月), 全盘木势
    - 炎上格 (火): 火旺于夏 (巳午未月), 全盘火势
    - 稼穑格 (土): 土旺四季 (辰戌丑未月), 全盘土势
    - 从革格 (金): 金旺于秋 (申酉戌月), 全盘金势
    - 润下格 (水): 水旺于冬 (亥子丑月), 全盘水势

    返回:
        格局字典或 None (不满足条件)
    """
    day_gan = four_pillars["day"]["gan"]
    dm_wx = GAN_WUXING_LIST[_gan_index(day_gan)]
    month_zhi = four_pillars["month"]["zhi"]

    zhuanwang_names = {
        "木": "曲直格",
        "火": "炎上格",
        "土": "稼穑格",
        "金": "从革格",
        "水": "润下格",
    }

    season_map = {
        "木": ["寅", "卯", "辰"],  # 春
        "火": ["巳", "午", "未"],  # 夏
        "金": ["申", "酉", "戌"],  # 秋
        "水": ["亥", "子", "丑"],  # 冬
        "土": ["辰", "戌", "丑", "未"],  # 四季
    }

    # 检查月令是否在该五行旺的季节
    required_zhi = season_map.get(dm_wx, [])
    if month_zhi not in required_zhi:
        return None

    # 统计全盘五行分布
    wx_counts = _count_wuxing_in_pillars(four_pillars)
    total = sum(wx_counts.values())
    same_count = wx_counts.get(dm_wx, 0)

    # 专旺格要求: 同五行占比 >= 60%，且无克我五行 (官杀)
    ratio = same_count / total if total > 0 else 0
    ke_wo_wx = WUXING_BEI_KE.get(dm_wx, "")
    ke_wo_count = wx_counts.get(ke_wo_wx, 0)

    if ratio >= 0.6 and ke_wo_count <= 1:
        ge_name = zhuanwang_names.get(dm_wx, "专旺格")
        return {
            "type": "专旺格",
            "name": ge_name,
            "analysis": (
                f"日主{dm_wx}生于{month_zhi}月，当令得时。"
                f"全盘{dm_wx}势独旺(占比{ratio:.0%})，"
                f"无官杀破格，成{ge_name}。"
                f"喜生扶，忌克泄。"
            ),
        }

    return None


# =============================================================================
# 从格判定
# =============================================================================

def _check_cong_ge(four_pillars: dict, strength: dict) -> dict:
    """
    判定变格 (从格)。

    条件: 日主极弱无根，某一行或几行极旺。

    类型:
    - 从强格: 印比极旺，日主不得不从
    - 从杀格: 七杀极旺，日主不得不从
    - 从财格: 财星极旺，日主不得不从
    - 从儿格: 食伤极旺，日主不得不从
    """
    score = strength.get("score", 50)
    if score > 25:
        return None  # 不够弱，不构成从格

    day_gan = four_pillars["day"]["gan"]
    dm_wx = GAN_WUXING_LIST[_gan_index(day_gan)]

    # 统计十神分布
    from .shishen_calc import get_all_shishen_mapping
    shishen_map = get_all_shishen_mapping(day_gan)

    # 在四柱中统计各十神的出现次数
    shishen_counts = {}
    for pkey, pillar in four_pillars.items():
        if pkey == "day":
            continue
        gan = pillar.get("gan", "")
        ss = shishen_map.get(gan, "")
        shishen_counts[ss] = shishen_counts.get(ss, 0) + 1

        # 藏干也计0.5
        canggan = pillar.get("canggan", [])
        if isinstance(canggan, list):
            for cg in canggan:
                cg_name = cg if isinstance(cg, str) else cg[0] if isinstance(cg, (tuple, list)) else str(cg)
                ss2 = shishen_map.get(cg_name, "")
                shishen_counts[ss2] = shishen_counts.get(ss2, 0) + 0.5

    # 找最多的十神
    if not shishen_counts:
        return None

    max_ss = max(shishen_counts, key=shishen_counts.get)
    max_count = shishen_counts[max_ss]

    cong_ge_map = {
        "七杀": "从杀格",
        "正官": "从杀格",
        "正财": "从财格",
        "偏财": "从财格",
        "食神": "从儿格",
        "伤官": "从儿格",
        "正印": "从强格",
        "偏印": "从强格",
        "比肩": "从强格",
        "劫财": "从强格",
    }

    ge_name = cong_ge_map.get(max_ss, "从弱格")

    return {
        "type": "变格",
        "name": ge_name,
        "analysis": (
            f"日主{dm_wx}极弱无根(评分{score})，{max_ss}极旺，"
            f"日主不得不从，成{ge_name}。"
            f"喜顺从旺神，忌生扶日主。"
        ),
    }


# =============================================================================
# 主判格局函数
# =============================================================================

def determine_geju(four_pillars: dict, strength: dict) -> dict:
    """
    判定八字格局类型。

    判定顺序:
    1. 先检查是否为专旺格 (一方五行极旺)
    2. 再检查是否为变格/从格 (日主极弱)
    3. 否则按正格 (八格) 判定

    参数:
        four_pillars: 四柱数据
        strength: 身强身弱判定结果 (来自 wuxing_calc.determine_strength)

    返回:
        {"type": "正格/变格/专旺格", "name": "正官格", "analysis": "..."}
    """
    # 1. 检查专旺格
    zhuanwang = _check_zhuanwang(four_pillars)
    if zhuanwang:
        return zhuanwang

    # 2. 检查从格
    cong_ge = _check_cong_ge(four_pillars, strength)
    if cong_ge:
        return cong_ge

    # 3. 正格判定
    return _determine_zhengge(four_pillars)
