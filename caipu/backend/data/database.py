"""MySQL 数据库连接管理"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_CHARSET


def _connect():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        charset=MYSQL_CHARSET,
        cursorclass=DictCursor
    )


@contextmanager
def get_db():
    """数据库连接上下文管理器"""
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def check_db():
    """健康检查"""
    try:
        conn = _connect()
        conn.close()
        return True
    except Exception:
        return False


def init_db():
    """建表（读取 init.sql）"""
    sql_path = os.path.join(os.path.dirname(__file__), '..', '..', 'init.sql')
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn = _connect()
    try:
        # 去掉 FOREIGN_KEY_CHECKS 行（在 context manager 里逐条执行更安全）
        for statement in sql.split(';'):
            stmt = statement.strip()
            if not stmt or stmt.startswith('--') or 'FOREIGN_KEY_CHECKS' in stmt:
                continue
            if stmt.upper().startswith('CREATE DATABASE') or stmt.upper().startswith('USE '):
                continue
            conn.cursor().execute(stmt)
        conn.commit()
    finally:
        conn.close()
