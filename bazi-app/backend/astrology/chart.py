"""
星盘主编排函数
==============
整合所有星历、宫位、相位模块，生成完整星盘。
"""

from .ephemeris import calc_all_planets, _julian_day, calc_sun_longitude
from .houses import calc_houses
from .aspects import calc_aspects, detect_aspect_patterns
from .constants import get_sign_by_degree, ZODIAC_SIGNS, PLANETS, HOUSES
from .analysis import analyze_chart


def calculate_chart(year, month, day, hour=0, minute=0,
                    longitude=116.4, latitude=39.9, timezone_offset=8.0,
                    name="", gender=""):
    """
    计算完整星盘。

    参数:
        year, month, day: 出生日期 (公历)
        hour, minute: 出生时间 (本地时间，24小时制)
        longitude: 出生地经度 (东经为正)，默认北京 116.4
        latitude: 出生地纬度 (北纬为正)，默认北京 39.9
        timezone_offset: 时区偏移 (小时)，默认东八区 +8
        name: 姓名 (可选)
        gender: 性别 (可选)

    返回:
        {
            "name": str,
            "gender": str,
            "birth_datetime": "YYYY-MM-DD HH:mm",
            "birth_location": {"longitude": float, "latitude": float, "timezone": float},
            "planets": [{name_cn, sign, sign_symbol, degree_in_sign, house, lon, ...}, ...],
            "houses": [{number, name_cn, cusp_degree, sign, sign_symbol, keywords}, ...],
            "angles": {ascendant, midheaven, descendant, imum_coeli},
            "aspects": [{...}, ...],
            "patterns": [str, ...],
            "analysis": {elements: {...}, modalities: {...}, ...},
        }
    """
    # 转换为 UTC 时间用于 JD 计算
    utc_hour = hour - timezone_offset + minute / 60.0
    jd = _julian_day(year, month, day, utc_hour)

    # === 行星位置 ===
    all_planets = calc_all_planets(jd)
    # jd1 = _julian_day(year, month, day, utc_hour + 1/24.0)
    # all_planets1 = calc_all_planets(jd1)  # 用于逆行判定

    # 给每个行星添加星座和宫位信息
    for p in all_planets:
        sign = get_sign_by_degree(p["lon"])
        p["sign"] = sign["name_cn"]
        p["sign_symbol"] = sign["symbol"]
        p["sign_element"] = sign["element"]
        p["sign_modality"] = sign["modality"]
        p["degree_in_sign"] = round(p["lon"] % 30, 2)
        p["lon"] = round(p["lon"], 4)

    # === 宫位系统 ===
    houses_data = calc_houses(jd, longitude, latitude)
    angles = {
        "ascendant": houses_data["ascendant"],
        "ascendant_sign": get_sign_by_degree(houses_data["ascendant"])["name_cn"],
        "ascendant_symbol": get_sign_by_degree(houses_data["ascendant"])["symbol"],
        "midheaven": houses_data["midheaven"],
        "midheaven_sign": get_sign_by_degree(houses_data["midheaven"])["name_cn"],
        "midheaven_symbol": get_sign_by_degree(houses_data["midheaven"])["symbol"],
        "descendant": houses_data["descendant"],
        "descendant_sign": get_sign_by_degree(houses_data["descendant"])["name_cn"],
        "imum_coeli": houses_data["imum_coeli"],
        "imum_coeli_sign": get_sign_by_degree(houses_data["imum_coeli"])["name_cn"],
        "lst": houses_data["lst"],
    }

    # === 行星落宫位 ===
    for p in all_planets:
        house_num = _find_planet_house(p["lon"], houses_data["cusp_degrees"])
        p["house"] = house_num
        p["house_name"] = HOUSES[house_num - 1]["name_cn"] if house_num else ""

    # === 相位 ===
    aspects = calc_aspects(all_planets)

    # === 格局 ===
    patterns = detect_aspect_patterns(aspects, all_planets)

    # === 元素/模式分析 ===
    analysis = analyze_chart(all_planets)

    return {
        "name": name,
        "gender": gender,
        "birth_datetime": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}",
        "birth_location": {
            "longitude": longitude,
            "latitude": latitude,
            "timezone": timezone_offset,
        },
        "planets": all_planets,
        "houses": houses_data["houses"],
        "angles": angles,
        "aspects": aspects,
        "patterns": patterns,
        "analysis": analysis,
    }


def _find_planet_house(lon, cusp_degrees):
    """
    根据黄经确定行星所在的宫位。
    宫位从宫头开始，按黄经升序排列。
    """
    if not cusp_degrees or len(cusp_degrees) != 12:
        return None

    for i in range(12):
        start = cusp_degrees[i]
        end = cusp_degrees[(i + 1) % 12]
        # 处理跨 0° 的情况
        if start <= end:
            if start <= lon < end:
                return i + 1
        else:
            if lon >= start or lon < end:
                return i + 1

    return None
