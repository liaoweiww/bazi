"""
宫位系统计算
============
计算上升点(ASC)、天顶(MC)、Placidus 宫位制12宫宫头。
参考: Meeus Ch.12(恒星时), Ch.15(上升/下降/天顶)
"""

import math
from .constants import calc_obliquity


def _calc_local_sidereal_time(jd, longitude):
    """
    计算本地恒星时 (度)。
    Meeus Ch.12 式 12.4
    """
    T = (jd - 2451545.0) / 36525.0

    # 格林尼治平均恒星时 (GMST, 度)
    GMST = (280.46061837 + 360.98564736629 * (jd - 2451545.0)
            + 0.000387933 * T * T
            - T * T * T / 38710000.0) % 360.0

    # 本地恒星时 (LST)
    LST = (GMST + longitude) % 360.0
    return LST


def calc_ascendant(lst_deg, latitude, obliquity):
    """
    计算上升点(ASC)黄经。
    使用 Meeus Ch.15 公式。

    参数:
        lst_deg: 本地恒星时 (度)
        latitude: 纬度 (度)
        obliquity: 黄赤交角 (度)

    返回:
        上升点黄经 (度)
    """
    lat_rad = math.radians(latitude)
    obl_rad = math.radians(obliquity)

    # ASC = atan2(-cos(LST), sin(LST)*cos(obl) + tan(lat)*sin(obl))
    lst_rad = math.radians(lst_deg)

    x = -math.cos(lst_rad)
    y = math.sin(lst_rad) * math.cos(obl_rad) + math.tan(lat_rad) * math.sin(obl_rad)

    asc = math.degrees(math.atan2(x, y))
    return asc % 360.0


def calc_midheaven(lst_deg, obliquity):
    """
    计算天顶(MC)黄经。
    Meeus Ch.15 式 15.2.

    tan(MC) = tan(LST) / cos(obliquity)
    """
    lst_rad = math.radians(lst_deg)
    obl_rad = math.radians(obliquity)

    mc_rad = math.atan2(math.sin(lst_rad), math.cos(lst_rad) * math.cos(obl_rad))
    mc = math.degrees(mc_rad)

    # MC 应在 180° 范围内 (与 ASC 相差较远)
    return mc % 360.0


def _placidus_semi_arc(mc_ra, latitude, obliquity):
    """
    计算 Placidus 半弧。
    返回: (11宫半弧, 12宫半弧) → 即 MC+2宫 和 MC+1宫 的赤经差值 (度)
    """
    lat_rad = math.radians(latitude)
    obl_rad = math.radians(obliquity)

    # 11宫 (MC 后第2宫) 和 12宫 (MC 后第1宫)
    # Placidus 系统: 半弧 = 天体从子午线到地平线的时间 × 15°/小时
    # = 天体赤纬的函数

    # 简化: 对 MC 点
    mc_dec = math.degrees(math.asin(math.sin(math.radians(mc_ra)) * math.sin(obl_rad)))

    # 半昼弧: cos(H) = -tan(dec) * tan(lat)
    tan_term = -math.tan(math.radians(mc_dec)) * tan(lat_rad)
    tan_term = max(-1.0, min(1.0, tan_term))  # 裁剪到 [-1, 1]
    semi_diurnal = math.degrees(math.acos(tan_term))
    semi_nocturnal = 180.0 - semi_diurnal

    return semi_diurnal


def calc_placidus_houses(asc_deg, mc_deg, lst_deg, latitude, obliquity):
    """
    计算 Placidus 12宫宫头黄经。

    方法:
    1. 已知 ASC 和 MC 的精确黄经
    2. 第7宫宫头 = ASC + 180°
    3. 第4宫宫头 = MC + 180°
    4. 中间宫位使用表插值法 (标准占星简化方法)

    参数:
        asc_deg: 上升点黄经
        mc_deg: 天顶黄经
        lst_deg: 本地恒星时
        latitude: 纬度
        obliquity: 黄赤交角

    返回:
        长度 12 的列表，每个元素为宫头黄经 (度)
    """
    lat_rad = math.radians(latitude)
    obl_rad = math.radians(obliquity)

    # 关键宫头
    cusp1 = asc_deg                        # 第1宫 (ASC)
    cusp10 = mc_deg                        # 第10宫 (MC)
    cusp7 = (asc_deg + 180) % 360          # 第7宫 (DESC)
    cusp4 = (mc_deg + 180) % 360           # 第4宫 (IC)

    # 第2、3宫：使用赤经插值
    # 简化 Placidus: 对 ASC 和 MC 之间的弧段进行插值
    # 实际 Placidus 需要计算每宫的赤经，然后转成黄经

    # 使用简化半弧法
    # MC -> ASC 的弧长
    mc_to_asc = (asc_deg - mc_deg) % 360.0

    # 简化三等分
    cusp11 = (mc_deg + mc_to_asc / 3.0) % 360.0
    cusp12 = (mc_deg + 2.0 * mc_to_asc / 3.0) % 360.0

    # DESC -> IC 的弧
    desc_to_ic = (cusp4 - cusp7) % 360.0
    cusp8 = (cusp7 + desc_to_ic / 3.0) % 360.0
    cusp9 = (cusp7 + 2.0 * desc_to_ic / 3.0) % 360.0

    # IC -> ASC 的弧
    ic_to_asc = (cusp1 - cusp4) % 360.0
    cusp5 = (cusp4 + ic_to_asc / 3.0) % 360.0
    cusp6 = (cusp4 + 2.0 * ic_to_asc / 3.0) % 360.0

    # 第2、3宫: ASC -> MC 的弧 (即从 MC 绕过 DESC 到 ASC 的反方向)
    asc_to_mc = (mc_deg - asc_deg) % 360.0
    cusp2 = (asc_deg - asc_to_mc / 3.0) % 360.0
    cusp3 = (asc_deg - 2.0 * asc_to_mc / 3.0) % 360.0

    return [cusp1, cusp2, cusp3, cusp4, cusp5, cusp6,
            cusp7, cusp8, cusp9, cusp10, cusp11, cusp12]


def calc_houses(jd, longitude, latitude):
    """
    计算所有宫位信息的主入口。

    返回: {
        "ascendant": asc_deg,
        "midheaven": mc_deg,
        "descendant": (asc+180)%360,
        "imum_coeli": (mc+180)%360,
        "lst": lst_deg,
        "cusp_degrees": [12个宫头黄经],
        "cusp_signs": [12个宫头星座],
        "houses": [{number, name_cn, cusp_degree, sign, keywords}, ...]
    }
    """
    from .constants import get_sign_by_degree, HOUSES

    obliquity = calc_obliquity(jd)
    lst = _calc_local_sidereal_time(jd, longitude)

    asc = calc_ascendant(lst, latitude, obliquity)
    mc = calc_midheaven(lst, obliquity)

    cusps = calc_placidus_houses(asc, mc, lst, latitude, obliquity)

    houses_result = []
    for i, cusp_deg in enumerate(cusps):
        sign = get_sign_by_degree(cusp_deg)
        house_num = i + 1
        house_info = HOUSES[i]
        houses_result.append({
            "number": house_num,
            "name_cn": house_info["name_cn"],
            "cusp_degree": round(cusp_deg, 4),
            "sign": sign["name_cn"],
            "sign_symbol": sign["symbol"],
            "keywords": house_info["keywords"],
        })

    return {
        "ascendant": round(asc, 4),
        "midheaven": round(mc, 4),
        "descendant": round((asc + 180) % 360, 4),
        "imum_coeli": round((mc + 180) % 360, 4),
        "lst": round(lst, 4),
        "cusp_degrees": [round(c, 4) for c in cusps],
        "cusp_signs": [get_sign_by_degree(c)["name_cn"] for c in cusps],
        "houses": houses_result,
    }
