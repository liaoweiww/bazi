"""
SQLite 数据库管理模块
======================
提供数据库连接、初始化、表创建等功能。
使用上下文管理器确保连接安全关闭。
"""

import sqlite3
import os
from contextlib import contextmanager

# 数据库文件路径：data/bazi.db，相对于本文件所在目录
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "bazi.db")


@contextmanager
def get_db():
    """
    数据库连接上下文管理器。

    用法:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(...)

    自动处理连接关闭和异常回滚。
    """
    conn = sqlite3.connect(DB_PATH)
    # 启用外键约束
    conn.execute("PRAGMA foreign_keys = ON")
    # 返回字典形式的行，方便按列名访问
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """
    初始化数据库：创建所有基础表（如果不存在）。

    共6张表：
      1. tiangan   - 十天干
      2. dizhi     - 十二地支
      3. jiazi     - 六十甲子
      4. shishen_map - 十神映射
      5. wuxing_relation - 五行生克关系
      6. wannianli - 万年历（日期-干支对应）

    该函数可重复调用，已存在的表不会被重建。
    """
    # 确保 data 目录存在
    os.makedirs(DB_DIR, exist_ok=True)

    with get_db() as conn:
        cursor = conn.cursor()

        # ---- 表1：十天干 ----
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tiangan (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,        -- 甲、乙、丙、丁、戊、己、庚、辛、壬、癸
                full_name TEXT,                    -- 甲木、乙木...
                yin_yang TEXT NOT NULL,           -- 阳/阴
                wuxing TEXT NOT NULL,             -- 木/火/土/金/水
                direction TEXT,                    -- 东/南/中/西/北
                nature TEXT,                       -- 性情描述
                color TEXT                         -- 青/赤/黄/白/黑
            )
        """)

        # ---- 表2：十二地支 ----
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dizhi (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,        -- 子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥
                yin_yang TEXT NOT NULL,
                wuxing TEXT NOT NULL,
                canggan TEXT NOT NULL,            -- 藏干列表 JSON: ["甲","丙","戊"]
                benqi TEXT NOT NULL,              -- 本气
                yuqi TEXT,                        -- 余气 JSON
                direction TEXT,
                shichen TEXT,                     -- 对应时辰
                shengxiao TEXT,                   -- 生肖
                month_number INTEGER              -- 农历月份(寅=1)
            )
        """)

        # ---- 表3：六十甲子 ----
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jiazi (
                id INTEGER PRIMARY KEY,
                seq INTEGER NOT NULL UNIQUE,       -- 序号1-60
                ganzhi TEXT NOT NULL UNIQUE,       -- 甲子、乙丑...
                tiangan TEXT NOT NULL,
                dizhi TEXT NOT NULL,
                nayin TEXT NOT NULL,               -- 纳音五行 如"海中金"
                nayin_wuxing TEXT NOT NULL         -- 纳音五行属性 金/木/水/火/土
            )
        """)

        # ---- 表4：十神映射 ----
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shishen_map (
                id INTEGER PRIMARY KEY,
                ri_gan TEXT NOT NULL,              -- 日干（我）
                other_gan TEXT NOT NULL,           -- 他干
                shishen TEXT NOT NULL,             -- 十神名称
                yin_yang_same BOOLEAN,            -- 阴阳相同
                wuxing_relation TEXT              -- 五行关系：生/克/比
            )
        """)

        # ---- 表5：五行生克关系 ----
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wuxing_relation (
                id INTEGER PRIMARY KEY,
                from_wx TEXT NOT NULL,             -- 来源五行
                to_wx TEXT NOT NULL,               -- 目标五行
                relation TEXT NOT NULL             -- 生/克
            )
        """)

        # ---- 表6：万年历 ----
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wannianli (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                solar_date TEXT NOT NULL,          -- YYYY-MM-DD
                lunar_year INTEGER,
                lunar_month INTEGER,
                lunar_day INTEGER,
                leap_month BOOLEAN DEFAULT 0,
                ganzhi_year TEXT,                  -- 年柱干支
                ganzhi_month TEXT,                 -- 月柱干支
                ganzhi_day TEXT,                   -- 日柱干支
                solar_term TEXT,                   -- 最近节气
                solar_term_date TEXT               -- 节气日期
            )
        """)


# 如果直接运行此文件，则自动初始化数据库
if __name__ == "__main__":
    init_db()
    print(f"数据库已初始化: {DB_PATH}")
