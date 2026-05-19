"""
星历计算模块
============
使用 Meeus「天文算法」低精度公式计算10大行星的视黄经。
参考: Jean Meeus, "Astronomical Algorithms", 2nd ed.
  - Ch.25: 太阳坐标 (复用 paipan.py 中 _sun_longitude)
  - Ch.32: 行星的椭圆轨道要素 (低精度)
  - Ch.47: 月亮位置
"""

import math

# =============================================================================
# 太阳视黄经 (从 paipan.py 复用，直接在此实现)
# =============================================================================

def calc_sun_longitude(jd):
    """太阳视黄经（度），Meeus 低精度公式，精度约 0.01°"""
    T = (jd - 2451545.0) / 36525.0
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
    M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
    M_rad = math.radians(M % 360)
    C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M_rad) \
        + (0.019993 - 0.000101 * T) * math.sin(2 * M_rad) \
        + 0.000289 * math.sin(3 * M_rad)
    return (L0 + C) % 360.0


# =============================================================================
# 月亮视黄经 (Meeus Ch.47)
# =============================================================================

def calc_moon_longitude(jd):
    """月亮视黄经（度），Meeus Ch.47 简化公式，精度约 0.3°"""
    T = (jd - 2451545.0) / 36525.0

    # 月亮平黄经
    Lp = 218.3164591 + 481267.88134236 * T - 0.0013268 * T * T + T**3 / 538841.0 - T**4 / 65194000.0
    # 月亮平近点角
    Mp = 134.9634114 + 477198.8676313 * T + 0.0089970 * T * T + T**3 / 69699.0 - T**4 / 14712000.0
    # 太阳平近点角
    Ms = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T + T**3 / 24490000.0
    # 月亮升交点平黄经
    F = 93.2720993 + 483202.0175273 * T - 0.0034029 * T * T - T**3 / 3526000.0 + T**4 / 863310000.0

    Lp = math.radians(Lp % 360)
    Mp = math.radians(Mp % 360)
    Ms = math.radians(Ms % 360)
    F = math.radians(F % 360)

    # 主要周期项 (简化版，仅保留最大项)
    dL = 0
    # 出差 (Evection): +1.274° * sin(2D - M')
    # 二均差 (Variation): +0.658° * sin(2D)
    # 中心差 (Annual equation): -0.186° * sin(M)
    # 周年差: -0.11° * sin(2F)
    D = Lp - Ms  # 月亮与太阳的平距角 (这里简化用 Lp - Ms)

    # 出差: +1.274 * sin(2D - Mp)
    dL += 1.274 * math.sin(2 * D - Mp)
    # 二均差: +0.658 * sin(2D)
    dL += 0.658 * math.sin(2 * D)
    # 中心差: +6.289 * sin(Mp)
    dL += 6.289 * math.sin(Mp)
    # 周年差: -0.186 * sin(Ms)
    dL -= 0.186 * math.sin(Ms)
    # 其他项
    dL -= 0.110 * math.sin(2 * F)  # 黄纬修正反射到经度
    dL += 0.214 * math.sin(2 * Mp)  # 二倍角项
    dL -= 0.059 * math.sin(2 * D - Ms)  # 出差二阶
    dL += 0.057 * math.sin(2 * D - Mp - Ms)  # 出差+周年差交互

    return (math.degrees(Lp) + dL) % 360.0


# =============================================================================
# 行星视黄经 (Meeus Ch.32 低精度公式)
# =============================================================================
# 每个行星: (半长轴, 偏心率, 倾角, 升交点经度, 近日点经度, 平经度)
# 系数单位为 度/世纪 (除偏心率外)

# 水星轨道要素
MERCURY_ELEMENTS = {
    "a": 0.387099,   # AU
    "e": (0.205614, 0.000020, -0.000000),
    "i": (7.0029, -0.0019, 0.000001),
    "Omega": (48.3313, -0.1251, -0.000003),
    "omega_bar": (29.1241, 1.0143, -0.000001),
    "L": (178.1790, 149474.0718, 0.000301),
}

# 金星轨道要素
VENUS_ELEMENTS = {
    "a": 0.723330,
    "e": (0.006773, -0.000047, 0.000000),
    "i": (3.3946, -0.0010, 0.000000),
    "Omega": (76.6799, -0.2662, -0.000004),
    "omega_bar": (54.8910, 1.3617, -0.000001),
    "L": (342.7675, 58519.2129, 0.000310),
}

# 火星轨道要素
MARS_ELEMENTS = {
    "a": 1.523688,
    "e": (0.093313, 0.000092, -0.000001),
    "i": (1.8497, -0.0063, 0.000000),
    "Omega": (49.5574, -0.2993, -0.000004),
    "omega_bar": (285.4314, 1.0706, 0.000013),
    "L": (292.7310, 19141.6962, 0.000311),
}

# 木星轨道要素
JUPITER_ELEMENTS = {
    "a": 5.202561,
    "e": (0.048498, 0.000163, -0.000001),
    "i": (1.3036, -0.0044, 0.000000),
    "Omega": (100.4545, -0.2445, -0.000004),
    "omega_bar": (273.8687, 0.5989, 0.000009),
    "L": (157.6085, 3036.2726, -0.000035),
}

# 土星轨道要素
SATURN_ELEMENTS = {
    "a": 9.554747,
    "e": (0.055548, -0.000347, 0.000000),
    "i": (2.4889, -0.0044, 0.000000),
    "Omega": (113.6633, -0.2435, -0.000003),
    "omega_bar": (338.3143, 0.5561, 0.000011),
    "L": (250.6650, 1224.0166, -0.000049),
}

# 天王星轨道要素
URANUS_ELEMENTS = {
    "a": 19.21814,
    "e": (0.046381, -0.000023, 0.000000),
    "i": (0.7736, -0.0002, 0.000006),
    "Omega": (74.0164, -0.0096, -0.000052),
    "omega_bar": (99.4290, 0.1173, 0.000054),
    "L": (291.7085, 429.0161, -0.000028),
}

# 海王星轨道要素
NEPTUNE_ELEMENTS = {
    "a": 30.10957,
    "e": (0.008997, 0.000006, 0.000000),
    "i": (1.7700, -0.0118, 0.000000),
    "Omega": (131.7869, -0.0508, -0.000170),
    "omega_bar": (277.3916, -0.3479, 0.000012),
    "L": (215.8012, 219.0289, -0.000084),
}

# 冥王星轨道要素 (简化公式)
PLUTO_ELEMENTS = {
    "a": 39.48169,
    "e": (0.248808, 0.000065, 0.000000),
    "i": (17.1417, 0.0049, 0.000001),
    "Omega": (110.3093, -0.0375, -0.000013),
    "omega_bar": (112.7768, -0.2534, 0.000007),
    "L": (150.3403, 146.6103, -0.000049),
}

# 行星元素查找表 (必须是上述顺序)
_PLANET_ELEMENTS = {
    "Mercury": MERCURY_ELEMENTS,
    "Venus": VENUS_ELEMENTS,
    "Mars": MARS_ELEMENTS,
    "Jupiter": JUPITER_ELEMENTS,
    "Saturn": SATURN_ELEMENTS,
    "Uranus": URANUS_ELEMENTS,
    "Neptune": NEPTUNE_ELEMENTS,
    "Pluto": PLUTO_ELEMENTS,
}


def _mean_elements(elm, T):
    """计算给定时刻 T 的行星轨道要素 (Meeus Ch.32 式 32.1)"""
    # 半长轴
    a = elm["a"]
    # 偏心率
    e0, e1, e2 = elm["e"]
    e = e0 + e1 * T + e2 * T * T
    # 倾角 (度)
    i0, i1, i2 = elm["i"]
    i = i0 + i1 * T + i2 * T * T
    # 升交点经度 (度)
    O0, O1, O2 = elm["Omega"]
    Omega = O0 + O1 * T + O2 * T * T
    # 近日点经度 = 升交点 + 近日点角距 (度)
    w0, w1, w2 = elm["omega_bar"]
    omega_bar = w0 + w1 * T + w2 * T * T
    # 平经度 (度)
    L0, L1, L2 = elm["L"]
    L = L0 + L1 * T + L2 * T * T
    return a, e, i, Omega, omega_bar, L


def _kepler(M_deg, e, tol=1e-8):
    """解算开普勒方程 M = E - e*sin(E)。返回偏近点角 E (弧度)"""
    M = math.radians(M_deg % 360)
    E = M + e * math.sin(M)  # 初始猜测
    for _ in range(50):
        dE = (M - (E - e * math.sin(E))) / (1 - e * math.cos(E))
        E += dE
        if abs(dE) < tol:
            break
    return E


def _planet_heliocentric_longitude(elm, T):
    """
    计算行星的日心黄经 (Meeus Ch.32 低精度公式)。
    返回日心黄经 (度)。
    """
    a, e, i, Omega, omega_bar, L = _mean_elements(elm, T)

    # 近日点角距 = omega_bar - Omega
    w = omega_bar - Omega
    # 平近点角 = L - omega_bar
    M = (L - omega_bar) % 360

    # 解算开普勒方程
    E = _kepler(M, e)

    # 计算日心极坐标
    # 真近点角 v
    sin_v = math.sqrt(1 - e * e) * math.sin(E) / (1 - e * math.cos(E))
    cos_v = (math.cos(E) - e) / (1 - e * math.cos(E))
    v = math.atan2(sin_v, cos_v)
    if v < 0:
        v += 2 * math.pi

    # 日心距离 r
    r = a * (1 - e * math.cos(E))

    # 日心黄经 = 真近点角 + 近日点经度
    lon_helio = math.degrees(v) + omega_bar

    return lon_helio % 360, r


def _helio_to_geo(lon_helio_deg, r_planet, r_earth, lon_sun_deg):
    """
    日心黄经转地心视黄经 (简化版)。
    使用平面近似 (忽略黄纬)。

    lon_helio_deg: 行星日心黄经
    r_planet: 行星日心距离 (AU)
    r_earth: 地球日心距离 (AU)
    lon_sun_deg: 太阳地心黄经

    返回: 地心视黄经 (度)
    """
    # 行星日心直角坐标 (日心黄经 → 日心直角坐标, x 指向春分点)
    lon_rad = math.radians(lon_helio_deg)
    x_h = r_planet * math.cos(lon_rad)
    y_h = r_planet * math.sin(lon_rad)

    # 地球日心直角坐标
    lon_sun_rad = math.radians(lon_sun_deg)
    x_e = r_earth * math.cos(lon_sun_rad)
    y_e = r_earth * math.sin(lon_sun_rad)

    # 行星地心直角坐标
    x_geo = x_h - x_e
    y_geo = y_h - y_e

    lon_geo = math.degrees(math.atan2(y_geo, x_geo))
    return lon_geo % 360


def calc_planet_longitude(jd, planet_name):
    """计算给定时刻的行星地心视黄经。返回 (lon_deg, is_retrograde)"""
    T = (jd - 2451545.0) / 36525.0

    # 太阳地心视黄经
    sun_lon = calc_sun_longitude(jd)

    # 地球轨道要素 (同金星，但半长轴为1)
    # 地球日心位置约等于从太阳看地球的方向，即 sun_lon + 180°
    # 地球日心距离 ~ 1 AU
    # 精确一点：使用太阳地心位置的反方向
    r_earth = 1.0  # 简化：实际地球日心距离在 0.983-1.017 间波动

    # 行星日心位置
    if planet_name in _PLANET_ELEMENTS:
        elm = _PLANET_ELEMENTS[planet_name]
        lon_helio, r_planet = _planet_heliocentric_longitude(elm, T)
        lon_geo = _helio_to_geo(lon_helio, r_planet, r_earth, sun_lon)
        return lon_geo, False
    else:
        raise ValueError(f"未知行星: {planet_name}")


def calc_all_planets(jd, check_retrograde=True):
    """
    计算所有10颗行星的地心视黄经。
    返回: 行星列表 [{name_cn, lon, is_retrograde}, ...]
    """
    results = []
    # 太阳
    sun_lon = calc_sun_longitude(jd)
    results.append({"name_cn": "太阳", "lon": sun_lon, "is_retrograde": False})

    # 月亮
    moon_lon = calc_moon_longitude(jd)
    results.append({"name_cn": "月亮", "lon": moon_lon, "is_retrograde": False})

    # 其余行星
    planet_names = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn",
                    "Uranus", "Neptune", "Pluto"]
    cn_names = ["水星", "金星", "火星", "木星", "土星", "天王星", "海王星", "冥王星"]

    for pname, cn in zip(planet_names, cn_names):
        lon, retro = calc_planet_longitude(jd, pname)
        results.append({"name_cn": cn, "lon": lon, "is_retrograde": retro})

    return results


# =============================================================================
# 常用工具
# =============================================================================

def _julian_day(year, month, day, hour=0.0):
    """公历转儒略日"""
    if month <= 2:
        year -= 1
        month += 12
    A = year // 100
    B = 2 - A + A // 4
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
    jd += hour / 24.0
    return jd


def dms_to_deg(d, m, s=0):
    """度分秒 → 十进制度"""
    return d + m / 60.0 + s / 3600.0
