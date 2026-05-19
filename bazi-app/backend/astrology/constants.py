"""
星座占星常量定义
================
12星座、10行星、5种主要相位、4元素、3模式
"""

# =============================================================================
# 12星座
# =============================================================================

ZODIAC_SIGNS = [
    {"name_cn": "白羊座", "name_en": "Aries",       "symbol": "♈", "element": "火", "modality": "基本",
     "ruling_planet": "火星", "date_range": "3月21日-4月19日", "start": 0,   "degree_range": (0, 30)},
    {"name_cn": "金牛座", "name_en": "Taurus",       "symbol": "♉", "element": "土", "modality": "固定",
     "ruling_planet": "金星", "date_range": "4月20日-5月20日", "start": 30,  "degree_range": (30, 60)},
    {"name_cn": "双子座", "name_en": "Gemini",       "symbol": "♊", "element": "风", "modality": "变动",
     "ruling_planet": "水星", "date_range": "5月21日-6月21日", "start": 60,  "degree_range": (60, 90)},
    {"name_cn": "巨蟹座", "name_en": "Cancer",       "symbol": "♋", "element": "水", "modality": "基本",
     "ruling_planet": "月亮", "date_range": "6月22日-7月22日", "start": 90,  "degree_range": (90, 120)},
    {"name_cn": "狮子座", "name_en": "Leo",          "symbol": "♌", "element": "火", "modality": "固定",
     "ruling_planet": "太阳", "date_range": "7月23日-8月22日", "start": 120, "degree_range": (120, 150)},
    {"name_cn": "处女座", "name_en": "Virgo",        "symbol": "♍", "element": "土", "modality": "变动",
     "ruling_planet": "水星", "date_range": "8月23日-9月22日", "start": 150, "degree_range": (150, 180)},
    {"name_cn": "天秤座", "name_en": "Libra",        "symbol": "♎", "element": "风", "modality": "基本",
     "ruling_planet": "金星", "date_range": "9月23日-10月23日", "start": 180, "degree_range": (180, 210)},
    {"name_cn": "天蝎座", "name_en": "Scorpio",      "symbol": "♏", "element": "水", "modality": "固定",
     "ruling_planet": "冥王星", "date_range": "10月24日-11月22日", "start": 210, "degree_range": (210, 240)},
    {"name_cn": "射手座", "name_en": "Sagittarius",  "symbol": "♐", "element": "火", "modality": "变动",
     "ruling_planet": "木星", "date_range": "11月23日-12月21日", "start": 240, "degree_range": (240, 270)},
    {"name_cn": "摩羯座", "name_en": "Capricorn",    "symbol": "♑", "element": "土", "modality": "基本",
     "ruling_planet": "土星", "date_range": "12月22日-1月19日", "start": 270, "degree_range": (270, 300)},
    {"name_cn": "水瓶座", "name_en": "Aquarius",     "symbol": "♒", "element": "风", "modality": "固定",
     "ruling_planet": "天王星", "date_range": "1月20日-2月18日", "start": 300, "degree_range": (300, 330)},
    {"name_cn": "双鱼座", "name_en": "Pisces",       "symbol": "♓", "element": "水", "modality": "变动",
     "ruling_planet": "海王星", "date_range": "2月19日-3月20日", "start": 330, "degree_range": (330, 360)},
]


def get_sign_by_degree(lon_deg):
    """根据黄经度数获取星座"""
    idx = int(lon_deg % 360) // 30
    return ZODIAC_SIGNS[idx]


def get_sign_by_name(name_cn):
    for s in ZODIAC_SIGNS:
        if s["name_cn"] == name_cn:
            return s
    return None


# =============================================================================
# 10大行星
# =============================================================================

PLANETS = [
    {"name_cn": "太阳", "name_en": "Sun",       "symbol": "☉", "category": "发光体",   "orbit": None},
    {"name_cn": "月亮", "name_en": "Moon",      "symbol": "☽", "category": "发光体",   "orbit": None},
    {"name_cn": "水星", "name_en": "Mercury",   "symbol": "☿", "category": "个人行星", "orbit": None},
    {"name_cn": "金星", "name_en": "Venus",     "symbol": "♀", "category": "个人行星", "orbit": None},
    {"name_cn": "火星", "name_en": "Mars",      "symbol": "♂", "category": "个人行星", "orbit": None},
    {"name_cn": "木星", "name_en": "Jupiter",   "symbol": "♃", "category": "社会行星", "orbit": None},
    {"name_cn": "土星", "name_en": "Saturn",    "symbol": "♄", "category": "社会行星", "orbit": None},
    {"name_cn": "天王星", "name_en": "Uranus",  "symbol": "♅", "category": "世代行星", "orbit": None},
    {"name_cn": "海王星", "name_en": "Neptune", "symbol": "♆", "category": "世代行星", "orbit": None},
    {"name_cn": "冥王星", "name_en": "Pluto",   "symbol": "♇", "category": "世代行星", "orbit": None},
]

# 用于计算的顺序（对应 ephemeris 内部索引）
PLANET_ORDER = ["Sun", "Moon", "Mercury", "Venus", "Mars",
                "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

PLANET_LOOKUP = {p["name_en"]: p for p in PLANETS}
PLANET_CN_LOOKUP = {p["name_cn"]: p for p in PLANETS}


# =============================================================================
# 相位定义
# =============================================================================

ASPECT_TYPES = [
    {"name_cn": "合相",   "name_en": "Conjunction", "angle": 0,   "orb": 8,  "nature": "中性",
     "keyword": "融合",   "symbol": "☌"},
    {"name_cn": "六分相", "name_en": "Sextile",      "angle": 60,  "orb": 6,  "nature": "和谐",
     "keyword": "机会",   "symbol": "⚹"},
    {"name_cn": "四分相", "name_en": "Square",        "angle": 90,  "orb": 7,  "nature": "紧张",
     "keyword": "挑战",   "symbol": "□"},
    {"name_cn": "三分相", "name_en": "Trine",         "angle": 120, "orb": 8,  "nature": "和谐",
     "keyword": "天赋",   "symbol": "△"},
    {"name_cn": "对分相", "name_en": "Opposition",    "angle": 180, "orb": 8,  "nature": "紧张",
     "keyword": "对立",   "symbol": "☍"},
]


def get_aspect_type(angle_diff, orb_factor=1.0):
    """根据角度差确定相位类型。返回 (aspect_dict, actual_orb) 或 (None, None)"""
    for asp in ASPECT_TYPES:
        effective_orb = asp["orb"] * orb_factor
        diff = abs(angle_diff - asp["angle"])
        if diff > 180:
            diff = 360 - diff
        if diff <= effective_orb:
            return asp, round(diff, 2)
    return None, None


# =============================================================================
# 四元素
# =============================================================================

ELEMENTS = {
    "火": {"name_cn": "火象", "name_en": "Fire", "signs": ["白羊座", "狮子座", "射手座"],
           "traits": "热情、行动力、自信、创造力"},
    "土": {"name_cn": "土象", "name_en": "Earth", "signs": ["金牛座", "处女座", "摩羯座"],
           "traits": "务实、稳定、耐心、可靠"},
    "风": {"name_cn": "风象", "name_en": "Air", "signs": ["双子座", "天秤座", "水瓶座"],
           "traits": "理性、沟通、社交、灵活"},
    "水": {"name_cn": "水象", "name_en": "Water", "signs": ["巨蟹座", "天蝎座", "双鱼座"],
           "traits": "感性、直觉、情感、同理心"},
}

# =============================================================================
# 三种模式
# =============================================================================

MODALITIES = {
    "基本": {"name_cn": "基本星座", "name_en": "Cardinal", "signs": ["白羊座", "巨蟹座", "天秤座", "摩羯座"],
             "traits": "开创、主动、领导力"},
    "固定": {"name_cn": "固定星座", "name_en": "Fixed", "signs": ["金牛座", "狮子座", "天蝎座", "水瓶座"],
             "traits": "坚持、稳定、执着"},
    "变动": {"name_cn": "变动星座", "name_en": "Mutable", "signs": ["双子座", "处女座", "射手座", "双鱼座"],
             "traits": "适应、灵活、多变"},
}

# =============================================================================
# 12宫位
# =============================================================================

HOUSES = [
    {"number": 1,  "name_cn": "命宫",     "keywords": "自我、外貌、第一印象、人格面具"},
    {"number": 2,  "name_cn": "财帛宫",   "keywords": "财富、价值观、物质资源、自我价值"},
    {"number": 3,  "name_cn": "兄弟宫",   "keywords": "沟通、学习、短途旅行、兄弟姐妹"},
    {"number": 4,  "name_cn": "田宅宫",   "keywords": "家庭、根源、房产、安全感"},
    {"number": 5,  "name_cn": "子女宫",   "keywords": "创造力、恋爱、子女、娱乐"},
    {"number": 6,  "name_cn": "奴仆宫",   "keywords": "工作、健康、日常事务、服务"},
    {"number": 7,  "name_cn": "夫妻宫",   "keywords": "伴侣、合作、一对一关系、公开敌人"},
    {"number": 8,  "name_cn": "疾厄宫",   "keywords": "深层转变、他人资源、性、生死"},
    {"number": 9,  "name_cn": "迁移宫",   "keywords": "高等教育、旅行、哲学、信仰"},
    {"number": 10, "name_cn": "官禄宫",   "keywords": "事业、社会地位、名声、人生目标"},
    {"number": 11, "name_cn": "福德宫",   "keywords": "朋友、社群、理想、希望"},
    {"number": 12, "name_cn": "玄秘宫",   "keywords": "潜意识、灵性、隐秘、牺牲"},
]

# =============================================================================
# 逆行判定阈值 (每个行星的日心经度变化率接近零时判定)
# 用于简单判定：比较一段时间内的位置变化
# =============================================================================

# 黄赤交角近似公式系数 (Meeus Ch.22)
# 用于计算某时刻的赤道倾角
# obliq = 23°26'21.448" - 46.8150"*T - 0.00059"*T² + 0.001813"*T³
# 转换为度
def calc_obliquity(jd):
    """计算黄赤交角（度）"""
    T = (jd - 2451545.0) / 36525.0
    obl = 23.4392911 - 0.0130041667 * T - 0.0000001639 * T * T + 0.0000005036 * T * T * T
    return obl
