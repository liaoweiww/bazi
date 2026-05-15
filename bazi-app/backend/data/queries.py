"""
数据查询工具函数模块
====================
提供命理基础数据的便捷查询接口，包括天干、地支、六十甲子、十神、五行生克等。
所有函数均返回字典或字典列表，方便上层模块使用。
"""

import json
from data.database import get_db


# ============================================================
# 天干查询
# ============================================================

def get_tiangan(name: str) -> dict | None:
    """
    根据天干名称查询单条天干记录。

    参数:
        name: 天干名称，如 "甲"、"乙"
    返回:
        dict: 包含 id, name, full_name, yin_yang, wuxing, direction, nature, color
        None: 未找到时返回
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tiangan WHERE name = ?", (name,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_tiangan() -> list[dict]:
    """
    获取全部天干列表，按 id 排序。

    返回:
        list[dict]: 全部10条天干记录
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tiangan ORDER BY id")
        return [dict(row) for row in cursor.fetchall()]


# ============================================================
# 地支查询
# ============================================================

def get_dizhi(name: str) -> dict | None:
    """
    根据地支名称查询单条地支记录。

    参数:
        name: 地支名称，如 "子"、"寅"
    返回:
        dict: 包含完整地支信息（canggan/yuqi 字段已从 JSON 解析为列表）
        None: 未找到时返回
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dizhi WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row is None:
            return None
        result = dict(row)
        # 将 JSON 字符串字段反序列化为 Python 列表
        if result.get("canggan"):
            result["canggan"] = json.loads(result["canggan"])
        if result.get("yuqi"):
            result["yuqi"] = json.loads(result["yuqi"])
        return result


def get_all_dizhi() -> list[dict]:
    """
    获取全部地支列表，按 id 排序。

    返回:
        list[dict]: 全部12条地支记录（canggan/yuqi 已解析）
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dizhi ORDER BY id")
        rows = cursor.fetchall()
        results = []
        for row in rows:
            item = dict(row)
            if item.get("canggan"):
                item["canggan"] = json.loads(item["canggan"])
            if item.get("yuqi"):
                item["yuqi"] = json.loads(item["yuqi"])
            results.append(item)
        return results


def get_canggan(dizhi_name: str) -> list[str] | None:
    """
    获取指定地支的藏干列表。

    参数:
        dizhi_name: 地支名称，如 "寅" → ["甲","丙","戊"]
    返回:
        list[str]: 藏干列表（本气在前）
        None: 地支不存在时返回
    """
    dz = get_dizhi(dizhi_name)
    if dz is None:
        return None
    return dz.get("canggan", [])


# ============================================================
# 六十甲子查询
# ============================================================

def get_jiazi_by_ganzhi(ganzhi: str) -> dict | None:
    """
    根据干支组合查询六十甲子记录。

    参数:
        ganzhi: 干支名称，如 "甲子"、"癸亥"
    返回:
        dict: 包含 seq, ganzhi, tiangan, dizhi, nayin, nayin_wuxing
        None: 未找到时返回
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jiazi WHERE ganzhi = ?", (ganzhi,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_jiazi_by_seq(seq: int) -> dict | None:
    """
    根据序号(1-60)查询六十甲子记录。

    参数:
        seq: 序号，1-60
    返回:
        dict: 包含完整甲子信息
        None: 序号不合法时返回
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jiazi WHERE seq = ?", (seq,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_jiazi() -> list[dict]:
    """
    获取全部六十甲子列表，按序号排序。

    返回:
        list[dict]: 全部60条甲子记录
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jiazi ORDER BY seq")
        return [dict(row) for row in cursor.fetchall()]


# ============================================================
# 十神查询
# ============================================================

def get_shishen(ri_gan: str, other_gan: str) -> dict | None:
    """
    根据日干（我）和他干，查询十神关系。

    参数:
        ri_gan: 日干（代表命主自身），如 "甲"
        other_gan: 他干（四柱中的其他天干），如 "丙"
    返回:
        dict: {ri_gan, other_gan, shishen, yin_yang_same, wuxing_relation}
              例: {"ri_gan": "甲","other_gan": "丙","shishen": "食神",...}
        None: 无法确定关系时返回
    示例:
        get_shishen("甲", "丙") → "食神"（甲木生丙火，同阳）
        get_shishen("甲", "庚") → "七杀"（庚金克甲木，同阳）
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM shishen_map WHERE ri_gan = ? AND other_gan = ?",
            (ri_gan, other_gan)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


# ============================================================
# 五行生克查询
# ============================================================

def get_wuxing_relation(from_wx: str, to_wx: str) -> dict | None:
    """
    查询两个五行之间的生克关系。

    参数:
        from_wx: 来源五行（木/火/土/金/水）
        to_wx: 目标五行（木/火/土/金/水）
    返回:
        dict: {from_wx, to_wx, relation} 其中 relation 为 "生" 或 "克"
              例: {"from_wx": "木","to_wx": "火","relation": "生"}
        None: 无直接生克关系（如同五行）
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM wuxing_relation WHERE from_wx = ? AND to_wx = ?",
            (from_wx, to_wx)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


# ============================================================
# 辅助：验证数据库是否已初始化
# ============================================================

def is_database_ready() -> bool:
    """
    检查数据库是否已完成种子数据填充。

    通过查询天干表记录数来判断（应有10条）。

    返回:
        bool: 数据已就绪返回 True
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tiangan")
            count = cursor.fetchone()[0]
            return count >= 10
    except Exception:
        return False


# ============================================================
# 直接运行测试
# ============================================================
if __name__ == "__main__":
    # 简单自测：验证数据库状态和基础查询
    print("=== 数据查询模块自测 ===\n")

    if not is_database_ready():
        print("❌ 数据库未初始化，请先运行: python -m data.seed_data")
    else:
        # 测试天干查询
        tg = get_tiangan("甲")
        print(f"天干[甲]: {tg['full_name']}, {tg['yin_yang']}{tg['wuxing']}, 方位{tg['direction']}")

        # 测试地支查询
        dz = get_dizhi("寅")
        print(f"地支[寅]: 藏干={dz['canggan']}, 生肖={dz['shengxiao']}")

        # 测试甲子查询
        jz = get_jiazi_by_ganzhi("甲子")
        print(f"甲子[甲子]: 序号={jz['seq']}, 纳音={jz['nayin']}")

        # 测试十神查询
        ss = get_shishen("甲", "丙")
        print(f"十神(甲→丙): {ss['shishen']}")

        ss2 = get_shishen("甲", "庚")
        print(f"十神(甲→庚): {ss2['shishen']}")

        # 测试五行关系
        wx = get_wuxing_relation("木", "火")
        print(f"五行: 木→火 = {wx['relation']}")

        # 测试藏干
        cg = get_canggan("辰")
        print(f"地支辰藏干: {cg}")

        # 统计
        print(f"\n天干总数: {len(get_all_tiangan())}")
        print(f"地支总数: {len(get_all_dizhi())}")
        print(f"六十甲子总数: {len(get_all_jiazi())}")
        print("\n✅ 所有查询功能正常")
