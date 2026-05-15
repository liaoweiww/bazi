"""
真太阳时矫正模块 - True Solar Time Correction

八字排盘需要真太阳时，而非北京时间。真太阳时是基于太阳实际位置的当地时间。

算法流程:
  1. 平太阳时 = 标准时 + (经度 - 时区基准经度) × 4 分钟/度
     北京时间基准经度为东经120°
  2. 真太阳时 = 平太阳时 + 均时差(EoT)
  3. EoT 使用 Woolf 近似公式计算

均时差(Equation of Time)来源于:
  - 地球公转轨道为椭圆形（偏心率效应）
  - 地球自转轴倾斜（黄赤交角效应）

Woolf 近似公式 (精度约±1.7分钟):
  B = 360/365 × (N - 81)  # N为一年中的第几天，度数
  EoT = 9.87 × sin(2B) - 7.53 × cos(B) - 1.5 × sin(B)  # 分钟

更精确的公式 (Spencer, 1971, 精度约±0.5分钟):
  Γ = 2π × (N - 1) / 365  # 日角 (弧度)
  EoT = 229.18 × (0.000075 + 0.001868×cos(Γ) - 0.032077×sin(Γ)
                  - 0.014615×cos(2Γ) - 0.040849×sin(2Γ))  # 分钟

参考:
  - Woolf, H.M. (1968). "On the computation of solar elevation angles"
  - Spencer, J.W. (1971). "Fourier series representation of the position of the sun"
  - Jean Meeus, "Astronomical Algorithms"
"""

import math
from datetime import datetime, timedelta, timezone, date

__all__ = [
    "get_true_solar_time",
    "get_equation_of_time",
    "get_time_zone_offset",
    "get_time_zone_from_longitude",
]


# 时区基准经度: 北京时间 = UTC+8 = 东经120°
_BEIJING_BASE_LONGITUDE = 120.0

# 每分钟对应的经度差 (地球自转一周360° = 24小时 × 60分钟 = 1440分钟)
# 每1°经度 = 4 分钟, 每1′经度 = 4 秒
_MINUTES_PER_DEGREE = 4.0


def _day_of_year(dt):
    """
    计算某日期在一年中的第几天 (1-indexed: 1月1日 = 1)。

    参数:
        dt: datetime 或 date 对象

    返回:
        int: 一年中的第几天
    """
    if isinstance(dt, datetime):
        d = dt.date()
    else:
        d = dt
    # timetuple().tm_yday 返回 1-366
    return d.timetuple().tm_yday


def get_equation_of_time(dt):
    """
    计算指定日期的均时差 (Equation of Time)。

    使用 Spencer (1971) 傅里叶级数公式，精度约 ±0.5 分钟。
    比简单的 Woolf 公式更精确。

    均时差 = 视太阳时 - 平太阳时

    正值表示真太阳时比平太阳时快（太阳提前到达子午线），
    负值表示真太阳时比平太阳时慢。

    参数:
        dt: datetime 或 date 对象

    返回:
        float: 均时差（分钟）
    """
    N = _day_of_year(dt)

    # 日角 Γ (弧度) - Spencer 公式
    Gamma = 2 * math.pi * (N - 1) / 365.0

    # Spencer (1971) 傅里叶级数近似公式
    # 229.18 是将弧度转换为分钟时间的系数
    # = (24×60) / (2π) ≈ 229.183 分钟/弧度
    EoT = 229.18 * (
        0.000075
        + 0.001868 * math.cos(Gamma)
        - 0.032077 * math.sin(Gamma)
        - 0.014615 * math.cos(2 * Gamma)
        - 0.040849 * math.sin(2 * Gamma)
    )

    return EoT


def get_equation_of_time_woolf(dt):
    """
    使用 Woolf 近似公式计算均时差。
    这是请求规范中指定的公式，精度约 ±1.7 分钟。

    参数:
        dt: datetime 或 date 对象

    返回:
        float: 均时差（分钟）
    """
    N = _day_of_year(dt)

    # B = 360/365 × (N - 81) 度
    B = math.radians(360.0 / 365.0 * (N - 81))

    # Woolf 近似公式
    EoT = 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)

    return EoT


def get_time_zone_offset(longitude):
    """
    根据经度计算相对于 UTC 的时区偏移（小时）。

    地球划分为24个理论时区，每个时区跨15°经度。
    实际时区边界由各国政府规定（非纯几何划分）。

    参数:
        longitude: float, 经度 (东经为正, 西经为负)

    返回:
        float: 时区偏移（小时），如北京时间区 = 8.0
    """
    # 理论时区: 每15°一个时区
    # 基准: 0° (本初子午线) = UTC+0
    offset = round(longitude / 15.0)
    return float(offset)


def get_time_zone_from_longitude(longitude):
    """
    根据经度推断时区名称和偏移。
    这是一个近似函数，仅用于参考。

    参数:
        longitude: float, 经度

    返回:
        dict: {"zone_name": str, "utc_offset": float, "base_longitude": float}
    """
    offset = get_time_zone_offset(longitude)
    base_lon = offset * 15.0  # 时区基准经度

    sign = "+" if offset >= 0 else ""
    zone_name = f"UTC{sign}{int(offset):d}"

    return {
        "zone_name": zone_name,
        "utc_offset": offset,
        "base_longitude": base_lon,
    }


def get_true_solar_time(birth_time, longitude, latitude=None):
    """
    真太阳时矫正。

    将标准时间（如北京时间）转换为出生地的真太阳时。

    八字排盘必须以真太阳时为准，不能直接使用时钟时间。
    原因：
      - 中国统一使用北京时间（东八区），但全国横跨约60°经度
      - 乌鲁木齐（约87°E）的真太阳时比北京时间晚约2小时10分
      - 即使同经度，不同日期的均时差也不同（约±16分钟）

    算法:
      1. 平太阳时 = 北京时间 + (经度 - 120°) × 4 分钟
      2. 真太阳时 = 平太阳时 + 均时差

    参数:
        birth_time: datetime 对象（标准时间，如北京时间）
        longitude: float, 出生地经度（东经为正，度）
        latitude: float, 出生地纬度（北纬为正，度），可选参数
                  当前实现中纬度不直接影响真太阳时计算，
                  保留用于未来扩展（如日出日落时间）

    返回:
        datetime: 矫正后的真太阳时

    示例:
        >>> from datetime import datetime
        >>> # 北京时间 12:00, 成都 (104°E)
        >>> true_time = get_true_solar_time(datetime(2024, 6, 21, 12, 0), 104.07)
        >>> # 成都比北京晚约64分钟 + 均时差
    """
    if not isinstance(birth_time, datetime):
        raise TypeError(f"birth_time 必须是 datetime 对象, 收到 {type(birth_time)}")

    # ---- 步骤1: 平太阳时校正 ----
    # 北京时间以120°E为基准
    # 经度每向东1°, 时间早4分钟; 向西则晚4分钟
    longitude_offset_minutes = (longitude - _BEIJING_BASE_LONGITUDE) * _MINUTES_PER_DEGREE

    # 平太阳时
    mean_solar = birth_time + timedelta(minutes=longitude_offset_minutes)

    # ---- 步骤2: 均时差校正 ----
    # 使用 Spencer 精确公式
    eot_minutes = get_equation_of_time(birth_time)

    # 真太阳时 = 平太阳时 + 均时差
    true_solar = mean_solar + timedelta(minutes=eot_minutes)

    return true_solar


def get_true_solar_time_detailed(birth_time, longitude, latitude=None):
    """
    真太阳时矫正（返回详细信息版本）。

    参数:
        birth_time: datetime 对象（标准时间）
        longitude: float, 出生地经度
        latitude: float, 出生地纬度（可选）

    返回:
        dict:
            {
                "original_time": datetime,    # 原始时间
                "longitude_offset": float,     # 经度修正量（分钟）
                "eot": float,                  # 均时差（分钟）
                "mean_solar_time": datetime,   # 平太阳时
                "true_solar_time": datetime,   # 真太阳时
                "total_offset": float,         # 总修正量（分钟）
            }
    """
    longitude_offset_minutes = (longitude - _BEIJING_BASE_LONGITUDE) * _MINUTES_PER_DEGREE
    eot_minutes = get_equation_of_time(birth_time)
    total_offset = longitude_offset_minutes + eot_minutes

    mean_solar = birth_time + timedelta(minutes=longitude_offset_minutes)
    true_solar = mean_solar + timedelta(minutes=eot_minutes)

    return {
        "original_time": birth_time,
        "longitude": longitude,
        "latitude": latitude,
        "longitude_offset": round(longitude_offset_minutes, 2),
        "eot": round(eot_minutes, 2),
        "total_offset": round(total_offset, 2),
        "mean_solar_time": mean_solar,
        "true_solar_time": true_solar,
    }


def get_eot(date_obj):
    """
    计算指定日期的均时差（Equation of Time）。

    这是请求规范中指定的函数别名，返回分钟数。

    均时差产生原因:
      1. 地球椭圆轨道: 公转速度不均匀
         - 近日点(1月初)快, 远日点(7月初)慢
         - 导致太阳视运动速度变化
      2. 黄赤交角(23.44°): 太阳在黄道上匀速运动
         - 投影到赤道上产生不均匀
         - 二至点/二分点附近效应不同

    两个效应叠加，形成一年两负两正的均时差曲线:
      - 2月中旬约 -14 分钟 (太阳晚到, 正午偏晚)
      - 5月中旬约 +4 分钟 (太阳早到, 正午偏早)
      - 7月下旬约 -6 分钟
      - 11月初约 +16 分钟

    参数:
        date_obj: date 或 datetime 对象

    返回:
        float: 均时差（分钟）
    """
    return get_equation_of_time(date_obj)
