"""
喜用神与忌神判定
================
根据日主强弱、格局和调候需要，确定喜用神 (帮扶日主的五行十神)
和忌神 (不利日主的五行十神)。

基本原则:
1. 身强 → 喜克泄耗 (官杀、食伤、财星)
2. 身弱 → 喜生扶 (印星、比劫)
3. 调候: 冬月喜火暖局, 夏月喜水润局
"""

from ._constants import (
    GAN, GAN_WUXING_LIST,
    WUXING_SHENG, WUXING_KE,
    WUXING_BEI_SHENG, WUXING_BEI_KE,
    SEASON_ZHI,
)

from .shishen_calc import (
    calculate_shishen, get_shishen_wuxing, get_all_shishen_mapping,
)


def _gan_index(gan: str) -> int:
    return GAN.index(gan)


def _get_wuxing_relation(day_gan: str) -> dict:
    """
    获取日主与其他五行十神的关系映射。

    返回:
        {
            "木": "正官",  # 克我者
            "火": "正印",  # 生我者
            ...
        }
    """
    dm_wx = GAN_WUXING_LIST[_gan_index(day_gan)]

    # 对每种五行，找一个该五行的天干来计算十神
    wx_to_gan = {
        "木": "甲", "火": "丙", "土": "戊", "金": "庚", "水": "壬",
    }

    wx_relation = {}
    for wx, sample_gan in wx_to_gan.items():
        # 用阴干还是阳干不影响十神大类 (只是正/偏之别)
        # 这里取阳干代表
        ss = calculate_shishen(day_gan, sample_gan)
        # 归类
        if ss in ("正官", "七杀"):
            category = "官杀"
        elif ss in ("正印", "偏印"):
            category = "印星"
        elif ss in ("正财", "偏财"):
            category = "财星"
        elif ss in ("食神", "伤官"):
            category = "食伤"
        else:
            category = "比劫"
        wx_relation[wx] = category

    return wx_relation


def determine_yongji(four_pillars: dict, strength: dict, geju: dict) -> dict:
    """
    确定喜用神、忌神和闲神。

    参数:
        four_pillars: 四柱数据
        strength: 身强身弱结果 (来自 wuxing_calc.determine_strength)
        geju: 格局结果 (来自 geju.determine_geju)

    返回:
        {
            "yong_shen": [
                {"wuxing": "火", "shishen": "正印", "reason": "..."},
                ...
            ],
            "ji_shen": [...],
            "xian_shen": [...],
            "tiao_hou": "需要火来调候暖局"
        }
    """
    day_gan = four_pillars["day"]["gan"]
    dm_wx = GAN_WUXING_LIST[_gan_index(day_gan)]
    month_zhi = four_pillars["month"]["zhi"]
    level = strength.get("level", "中和")
    ge_type = geju.get("type", "正格")

    wx_relation = _get_wuxing_relation(day_gan)

    all_wuxing = ["木", "火", "土", "金", "水"]

    yong_shen = []
    ji_shen = []
    xian_shen = []

    # ---- 按身强身弱定喜忌 ----
    is_strong = "强" in level and "弱" not in level
    is_weak = "弱" in level and "强" not in level

    # 如果是专旺格或从格，喜忌不同
    if ge_type == "专旺格":
        # 专旺格: 喜生扶、忌克泄
        for wx in all_wuxing:
            rel = wx_relation.get(wx, "")
            if rel in ("印星", "比劫"):
                yong_shen.append({
                    "wuxing": wx, "shishen": rel,
                    "reason": f"专旺格喜生扶, {wx}为{rel}帮扶日主"
                })
            else:
                ji_shen.append({
                    "wuxing": wx, "shishen": rel,
                    "reason": f"专旺格忌克泄, {wx}破格"
                })
    elif ge_type == "变格":
        # 从格: 喜所从五行
        ge_name = geju.get("name", "")
        if "杀" in ge_name:
            favored = "官杀"
        elif "财" in ge_name:
            favored = "财星"
        elif "儿" in ge_name:
            favored = "食伤"
        else:
            favored = "印星"

        for wx in all_wuxing:
            rel = wx_relation.get(wx, "")
            if rel == favored or rel == "比劫":
                yong_shen.append({
                    "wuxing": wx, "shishen": rel,
                    "reason": f"从格喜顺旺神, {wx}为{rel}"
                })
            elif rel in ("印星", "比劫") and favored not in ("印星", "比劫"):
                ji_shen.append({
                    "wuxing": wx, "shishen": rel,
                    "reason": f"从格忌生扶日主破格"
                })
            else:
                xian_shen.append({
                    "wuxing": wx, "shishen": rel,
                    "reason": "从格中性"
                })
    elif is_strong:
        # 身强: 喜克泄耗
        for wx in all_wuxing:
            rel = wx_relation.get(wx, "")
            if rel in ("官杀", "食伤", "财星"):
                yong_shen.append({
                    "wuxing": wx, "shishen": rel,
                    "reason": f"日主{level}, 需{wx}({rel})来克泄耗平衡"
                })
            elif rel in ("印星", "比劫"):
                ji_shen.append({
                    "wuxing": wx, "shishen": rel,
                    "reason": f"日主{level}, 再生扶{wx}({rel})过旺"
                })
    elif is_weak:
        # 身弱: 喜生扶
        for wx in all_wuxing:
            rel = wx_relation.get(wx, "")
            if rel in ("印星", "比劫"):
                yong_shen.append({
                    "wuxing": wx, "shishen": rel,
                    "reason": f"日主{level}, 需{wx}({rel})生扶帮扶"
                })
            elif rel in ("官杀", "食伤"):
                ji_shen.append({
                    "wuxing": wx, "shishen": rel,
                    "reason": f"日主{level}, 再受{wx}({rel})克泄更弱"
                })
            elif rel == "财星":
                ji_shen.append({
                    "wuxing": wx, "shishen": rel,
                    "reason": f"日主{level}不担财, {wx}财来破印"
                })
    else:
        # 中和: 看格局需要
        for wx in all_wuxing:
            rel = wx_relation.get(wx, "")
            if wx != dm_wx:
                xian_shen.append({
                    "wuxing": wx, "shishen": rel,
                    "reason": "日主中和, 无所偏废"
                })

    # ---- 调候用神 ----
    tiao_hou = _determine_tiaohou(month_zhi, dm_wx)

    # 如果调候五行不在用神中，补充进用神
    if tiao_hou:
        tiao_wx = tiao_hou.get("wuxing", "")
        if tiao_wx:
            already_in_yong = any(y["wuxing"] == tiao_wx for y in yong_shen)
            if not already_in_yong:
                rel = wx_relation.get(tiao_wx, "")
                yong_shen.insert(0, {
                    "wuxing": tiao_wx,
                    "shishen": rel,
                    "reason": f"调候用神: {tiao_hou.get('reason', '')}"
                })

    return {
        "yong_shen": yong_shen,
        "ji_shen": ji_shen,
        "xian_shen": xian_shen,
        "tiao_hou": tiao_hou.get("reason", "") if tiao_hou else "",
    }


def _determine_tiaohou(month_zhi: str, dm_wx: str) -> dict:
    """
    根据出生月份判断调候需要。

    规则:
    - 冬月 (亥子丑): 金寒水冷，喜火调候暖局
    - 夏月 (巳午未): 火炎土燥，喜水调候润局
    - 秋月 (申酉戌): 金锐气寒，喜火炼金
    - 春月 (寅卯辰): 木旺之时，视五行定

    返回:
        {"wuxing": "火", "reason": "冬月金寒水冷需火暖局"}
        或 None (不需要调候)
    """
    winter = {"亥", "子", "丑"}
    summer = {"巳", "午", "未"}
    autumn = {"申", "酉", "戌"}

    if month_zhi in winter:
        return {"wuxing": "火", "reason": "冬月金寒水冷，急需火来调候暖局，以丙火为尊"}
    elif month_zhi in summer:
        return {"wuxing": "水", "reason": "夏月火炎土燥，急需水来调候润局，以壬癸为用"}
    elif month_zhi in autumn and dm_wx in ("金", "木"):
        return {"wuxing": "火", "reason": "秋月金气寒锐，需火暖金琢木，以丙丁为用"}

    return None
