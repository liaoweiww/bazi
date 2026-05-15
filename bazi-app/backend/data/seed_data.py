"""
种子数据填充模块
================
包含八字命理所有基础数据：天干、地支、六十甲子、十神映射、五行生克。
运行此文件即可将正统命理学数据一次性写入 bazi.db 数据库。
"""

import json
from data.database import get_db, init_db

# ============================================================
# 辅助常量
# ============================================================

# 天干 → 五行
TIANGAN_WUXING = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水",
}

# 天干 → 阴阳
TIANGAN_YINYANG = {
    "甲": "阳", "丙": "阳", "戊": "阳", "庚": "阳", "壬": "阳",
    "乙": "阴", "丁": "阴", "己": "阴", "辛": "阴", "癸": "阴",
}

# 五行生序：木→火→土→金→水→木
WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}

# 五行克序：木→土→水→火→金→木
WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}

# 天干顺序（用于生成六十甲子）
TIANGAN_LIST = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI_LIST = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 六十甲子纳音表：每相邻两个干支共用一个纳音
NAYIN_TABLE = [
    "海中金",   # 1甲子 2乙丑
    "炉中火",   # 3丙寅 4丁卯
    "大林木",   # 5戊辰 6己巳
    "路旁土",   # 7庚午 8辛未
    "剑锋金",   # 9壬申 10癸酉
    "山头火",   # 11甲戌 12乙亥
    "涧下水",   # 13丙子 14丁丑
    "城头土",   # 15戊寅 16己卯
    "白蜡金",   # 17庚辰 18辛巳
    "杨柳木",   # 19壬午 20癸未
    "泉中水",   # 21甲申 22乙酉
    "屋上土",   # 23丙戌 24丁亥
    "霹雳火",   # 25戊子 26己丑
    "松柏木",   # 27庚寅 28辛卯
    "长流水",   # 29壬辰 30癸巳
    "沙中金",   # 31甲午 32乙未
    "山下火",   # 33丙申 34丁酉
    "平地木",   # 35戊戌 36己亥
    "壁上土",   # 37庚子 38辛丑
    "金箔金",   # 39壬寅 40癸卯
    "覆灯火",   # 41甲辰 42乙巳
    "天河水",   # 43丙午 44丁未
    "大驿土",   # 45戊申 46己酉
    "钗钏金",   # 47庚戌 48辛亥
    "桑柘木",   # 49壬子 50癸丑
    "大溪水",   # 51甲寅 52乙卯
    "沙中土",   # 53丙辰 54丁巳
    "天上火",   # 55戊午 56己未
    "石榴木",   # 57庚申 58辛酉
    "大海水",   # 59壬戌 60癸亥
]


def _get_nayin(seq: int) -> str:
    """根据序号(1-60)获取纳音名称。每两个干支共用一个纳音。"""
    idx = (seq - 1) // 2  # 0-based index into NAYIN_TABLE
    return NAYIN_TABLE[idx]


def _get_nayin_wuxing(nayin: str) -> str:
    """从纳音名称中提取五行属性（取最后一个字，即 金/木/水/火/土）。"""
    return nayin[-1]


# ============================================================
# 天干种子数据
# ============================================================

TIANGAN_DATA = [
    {"id": 1,  "name": "甲", "full_name": "甲木", "yin_yang": "阳", "wuxing": "木",
     "direction": "东", "nature": "刚健正直，为栋梁之材", "color": "青"},
    {"id": 2,  "name": "乙", "full_name": "乙木", "yin_yang": "阴", "wuxing": "木",
     "direction": "东", "nature": "柔顺温和，如花草藤萝", "color": "青"},
    {"id": 3,  "name": "丙", "full_name": "丙火", "yin_yang": "阳", "wuxing": "火",
     "direction": "南", "nature": "热情奔放，如烈日当空", "color": "赤"},
    {"id": 4,  "name": "丁", "full_name": "丁火", "yin_yang": "阴", "wuxing": "火",
     "direction": "南", "nature": "文雅秀丽，如灯烛之光", "color": "赤"},
    {"id": 5,  "name": "戊", "full_name": "戊土", "yin_yang": "阳", "wuxing": "土",
     "direction": "中", "nature": "厚重诚实，如城墙之土", "color": "黄"},
    {"id": 6,  "name": "己", "full_name": "己土", "yin_yang": "阴", "wuxing": "土",
     "direction": "中", "nature": "谦卑包容，如田园之土", "color": "黄"},
    {"id": 7,  "name": "庚", "full_name": "庚金", "yin_yang": "阳", "wuxing": "金",
     "direction": "西", "nature": "刚强果断，如刀剑之金", "color": "白"},
    {"id": 8,  "name": "辛", "full_name": "辛金", "yin_yang": "阴", "wuxing": "金",
     "direction": "西", "nature": "细腻精致，如珠玉之金", "color": "白"},
    {"id": 9,  "name": "壬", "full_name": "壬水", "yin_yang": "阳", "wuxing": "水",
     "direction": "北", "nature": "智慧通达，如江河之水", "color": "黑"},
    {"id": 10, "name": "癸", "full_name": "癸水", "yin_yang": "阴", "wuxing": "水",
     "direction": "北", "nature": "内敛含蓄，如雨露之水", "color": "黑"},
]


# ============================================================
# 地支种子数据（含完整藏干）
# ============================================================

DIZHI_DATA = [
    {
        "id": 1, "name": "子", "yin_yang": "阳", "wuxing": "水",
        "canggan": json.dumps(["癸"], ensure_ascii=False),
        "benqi": "癸", "yuqi": None,
        "direction": "北", "shichen": "23:00-01:00",
        "shengxiao": "鼠", "month_number": 11,
    },
    {
        "id": 2, "name": "丑", "yin_yang": "阴", "wuxing": "土",
        "canggan": json.dumps(["己", "癸", "辛"], ensure_ascii=False),
        "benqi": "己", "yuqi": json.dumps(["癸", "辛"], ensure_ascii=False),
        "direction": "东北", "shichen": "01:00-03:00",
        "shengxiao": "牛", "month_number": 12,
    },
    {
        "id": 3, "name": "寅", "yin_yang": "阳", "wuxing": "木",
        "canggan": json.dumps(["甲", "丙", "戊"], ensure_ascii=False),
        "benqi": "甲", "yuqi": json.dumps(["丙", "戊"], ensure_ascii=False),
        "direction": "东北", "shichen": "03:00-05:00",
        "shengxiao": "虎", "month_number": 1,
    },
    {
        "id": 4, "name": "卯", "yin_yang": "阴", "wuxing": "木",
        "canggan": json.dumps(["乙"], ensure_ascii=False),
        "benqi": "乙", "yuqi": None,
        "direction": "东", "shichen": "05:00-07:00",
        "shengxiao": "兔", "month_number": 2,
    },
    {
        "id": 5, "name": "辰", "yin_yang": "阳", "wuxing": "土",
        "canggan": json.dumps(["戊", "乙", "癸"], ensure_ascii=False),
        "benqi": "戊", "yuqi": json.dumps(["乙", "癸"], ensure_ascii=False),
        "direction": "东南", "shichen": "07:00-09:00",
        "shengxiao": "龙", "month_number": 3,
    },
    {
        "id": 6, "name": "巳", "yin_yang": "阴", "wuxing": "火",
        "canggan": json.dumps(["丙", "戊", "庚"], ensure_ascii=False),
        "benqi": "丙", "yuqi": json.dumps(["戊", "庚"], ensure_ascii=False),
        "direction": "东南", "shichen": "09:00-11:00",
        "shengxiao": "蛇", "month_number": 4,
    },
    {
        "id": 7, "name": "午", "yin_yang": "阳", "wuxing": "火",
        "canggan": json.dumps(["丁", "己"], ensure_ascii=False),
        "benqi": "丁", "yuqi": json.dumps(["己"], ensure_ascii=False),
        "direction": "南", "shichen": "11:00-13:00",
        "shengxiao": "马", "month_number": 5,
    },
    {
        "id": 8, "name": "未", "yin_yang": "阴", "wuxing": "土",
        "canggan": json.dumps(["己", "丁", "乙"], ensure_ascii=False),
        "benqi": "己", "yuqi": json.dumps(["丁", "乙"], ensure_ascii=False),
        "direction": "西南", "shichen": "13:00-15:00",
        "shengxiao": "羊", "month_number": 6,
    },
    {
        "id": 9, "name": "申", "yin_yang": "阳", "wuxing": "金",
        "canggan": json.dumps(["庚", "壬", "戊"], ensure_ascii=False),
        "benqi": "庚", "yuqi": json.dumps(["壬", "戊"], ensure_ascii=False),
        "direction": "西南", "shichen": "15:00-17:00",
        "shengxiao": "猴", "month_number": 7,
    },
    {
        "id": 10, "name": "酉", "yin_yang": "阴", "wuxing": "金",
        "canggan": json.dumps(["辛"], ensure_ascii=False),
        "benqi": "辛", "yuqi": None,
        "direction": "西", "shichen": "17:00-19:00",
        "shengxiao": "鸡", "month_number": 8,
    },
    {
        "id": 11, "name": "戌", "yin_yang": "阳", "wuxing": "土",
        "canggan": json.dumps(["戊", "辛", "丁"], ensure_ascii=False),
        "benqi": "戊", "yuqi": json.dumps(["辛", "丁"], ensure_ascii=False),
        "direction": "西北", "shichen": "19:00-21:00",
        "shengxiao": "狗", "month_number": 9,
    },
    {
        "id": 12, "name": "亥", "yin_yang": "阴", "wuxing": "水",
        "canggan": json.dumps(["壬", "甲"], ensure_ascii=False),
        "benqi": "壬", "yuqi": json.dumps(["甲"], ensure_ascii=False),
        "direction": "西北", "shichen": "21:00-23:00",
        "shengxiao": "猪", "month_number": 10,
    },
]


# ============================================================
# 六十甲子种子数据（自动生成，确保准确性）
# ============================================================

def _build_jiazi_data():
    """
    自动生成六十甲子数据。
    天干地支按固定顺序循环组合，共60种（10和12的最小公倍数）。
    """
    jiazi_list = []
    for seq in range(1, 61):
        # 天干索引：(seq-1) % 10
        tg_idx = (seq - 1) % 10
        # 地支索引：(seq-1) % 12
        dz_idx = (seq - 1) % 12
        tg = TIANGAN_LIST[tg_idx]
        dz = DIZHI_LIST[dz_idx]
        ganzhi = tg + dz
        nayin = _get_nayin(seq)
        nayin_wx = _get_nayin_wuxing(nayin)
        jiazi_list.append({
            "id": seq,
            "seq": seq,
            "ganzhi": ganzhi,
            "tiangan": tg,
            "dizhi": dz,
            "nayin": nayin,
            "nayin_wuxing": nayin_wx,
        })
    return jiazi_list


# ============================================================
# 十神映射（自动推导 10日干 × 10他干 = 100条）
# ============================================================

def _determine_shishen(ri_gan: str, other_gan: str):
    """
    根据日干（我）和他干，推算十神名称。

    规则：
      - 同五行 + 同阴阳 → 比肩
      - 同五行 + 异阴阳 → 劫财
      - 他生我 + 同阴阳 → 偏印（枭神）
      - 他生我 + 异阴阳 → 正印
      - 我生他 + 同阴阳 → 食神
      - 我生他 + 异阴阳 → 伤官
      - 他克我 + 同阴阳 → 七杀（偏官）
      - 他克我 + 异阴阳 → 正官
      - 我克他 + 同阴阳 → 偏财
      - 我克他 + 异阴阳 → 正财
    """
    ri_wx = TIANGAN_WUXING[ri_gan]
    ri_yy = TIANGAN_YINYANG[ri_gan]
    ot_wx = TIANGAN_WUXING[other_gan]
    ot_yy = TIANGAN_YINYANG[other_gan]
    yy_same = (ri_yy == ot_yy)

    if ri_wx == ot_wx:
        # 同五行 → 比劫
        wuxing_rel = "比"
        if yy_same:
            return "比肩", yy_same, wuxing_rel
        else:
            return "劫财", yy_same, wuxing_rel
    elif WUXING_SHENG[ot_wx] == ri_wx:
        # 他生我 → 印星
        wuxing_rel = "生"
        if yy_same:
            return "偏印", yy_same, wuxing_rel
        else:
            return "正印", yy_same, wuxing_rel
    elif WUXING_SHENG[ri_wx] == ot_wx:
        # 我生他 → 食伤
        wuxing_rel = "生"
        if yy_same:
            return "食神", yy_same, wuxing_rel
        else:
            return "伤官", yy_same, wuxing_rel
    elif WUXING_KE[ot_wx] == ri_wx:
        # 他克我 → 官杀
        wuxing_rel = "克"
        if yy_same:
            return "七杀", yy_same, wuxing_rel
        else:
            return "正官", yy_same, wuxing_rel
    elif WUXING_KE[ri_wx] == ot_wx:
        # 我克他 → 财星
        wuxing_rel = "克"
        if yy_same:
            return "偏财", yy_same, wuxing_rel
        else:
            return "正财", yy_same, wuxing_rel
    else:
        raise ValueError(f"无法确定十神关系: ri_gan={ri_gan}, other_gan={other_gan}")


def _build_shishen_data():
    """生成完整的十神映射表（10×10=100条）。"""
    results = []
    seq_id = 1
    for ri_gan in TIANGAN_LIST:
        for other_gan in TIANGAN_LIST:
            shishen, yy_same, wx_rel = _determine_shishen(ri_gan, other_gan)
            results.append({
                "id": seq_id,
                "ri_gan": ri_gan,
                "other_gan": other_gan,
                "shishen": shishen,
                "yin_yang_same": yy_same,
                "wuxing_relation": wx_rel,
            })
            seq_id += 1
    return results


# ============================================================
# 五行生克关系数据
# ============================================================

def _build_wuxing_relation_data():
    """
    生成五行生克关系表。
    生：木→火、火→土、土→金、金→水、水→木
    克：木→土、土→水、水→火、火→金、金→木
    """
    wuxing_list = ["木", "火", "土", "金", "水"]
    results = []
    seq_id = 1
    for from_wx in wuxing_list:
        for to_wx in wuxing_list:
            if from_wx == to_wx:
                continue
            if WUXING_SHENG[from_wx] == to_wx:
                rel = "生"
            elif WUXING_KE[from_wx] == to_wx:
                rel = "克"
            else:
                continue  # 无直接生克关系则跳过
            results.append({
                "id": seq_id,
                "from_wx": from_wx,
                "to_wx": to_wx,
                "relation": rel,
            })
            seq_id += 1
    return results


# ============================================================
# 主入口：清空并重新填充所有种子数据
# ============================================================

def seed_all():
    """
    清空所有数据表并重新填充完整的命理基础数据。
    可重复运行，每次运行都会重置数据。
    """
    # 确保表结构存在
    init_db()

    with get_db() as conn:
        cursor = conn.cursor()

        # 清空所有表（按外键依赖倒序）
        cursor.execute("DELETE FROM wannianli")
        cursor.execute("DELETE FROM shishen_map")
        cursor.execute("DELETE FROM wuxing_relation")
        cursor.execute("DELETE FROM jiazi")
        cursor.execute("DELETE FROM dizhi")
        cursor.execute("DELETE FROM tiangan")

        # ---- 填充天干 ----
        for row in TIANGAN_DATA:
            cursor.execute(
                """INSERT INTO tiangan (id, name, full_name, yin_yang, wuxing, direction, nature, color)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (row["id"], row["name"], row["full_name"], row["yin_yang"],
                 row["wuxing"], row["direction"], row["nature"], row["color"])
            )
        print(f"  ✓ 天干数据: {len(TIANGAN_DATA)} 条")

        # ---- 填充地支 ----
        for row in DIZHI_DATA:
            cursor.execute(
                """INSERT INTO dizhi (id, name, yin_yang, wuxing, canggan, benqi, yuqi,
                         direction, shichen, shengxiao, month_number)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (row["id"], row["name"], row["yin_yang"], row["wuxing"],
                 row["canggan"], row["benqi"], row["yuqi"],
                 row["direction"], row["shichen"], row["shengxiao"], row["month_number"])
            )
        print(f"  ✓ 地支数据: {len(DIZHI_DATA)} 条")

        # ---- 填充六十甲子 ----
        jiazi_data = _build_jiazi_data()
        for row in jiazi_data:
            cursor.execute(
                """INSERT INTO jiazi (id, seq, ganzhi, tiangan, dizhi, nayin, nayin_wuxing)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (row["id"], row["seq"], row["ganzhi"], row["tiangan"],
                 row["dizhi"], row["nayin"], row["nayin_wuxing"])
            )
        print(f"  ✓ 六十甲子数据: {len(jiazi_data)} 条")

        # ---- 填充十神映射 ----
        shishen_data = _build_shishen_data()
        for row in shishen_data:
            cursor.execute(
                """INSERT INTO shishen_map (id, ri_gan, other_gan, shishen, yin_yang_same, wuxing_relation)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (row["id"], row["ri_gan"], row["other_gan"], row["shishen"],
                 row["yin_yang_same"], row["wuxing_relation"])
            )
        print(f"  ✓ 十神映射数据: {len(shishen_data)} 条")

        # ---- 填充五行生克关系 ----
        wx_rel_data = _build_wuxing_relation_data()
        for row in wx_rel_data:
            cursor.execute(
                """INSERT INTO wuxing_relation (id, from_wx, to_wx, relation)
                   VALUES (?, ?, ?, ?)""",
                (row["id"], row["from_wx"], row["to_wx"], row["relation"])
            )
        print(f"  ✓ 五行生克数据: {len(wx_rel_data)} 条")

    print("\n✅ 所有种子数据填充完成！")


# ============================================================
# 如果直接运行此文件，则自动执行数据填充
# ============================================================
if __name__ == "__main__":
    seed_all()
