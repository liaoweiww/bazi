import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DB_PATH = os.path.join(DB_DIR, 'caipu.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.executescript('''
        CREATE TABLE IF NOT EXISTS recipe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cover_image TEXT DEFAULT '',
            icon_image TEXT DEFAULT '',
            category TEXT NOT NULL DEFAULT '家常菜',
            cook_time INTEGER DEFAULT 30,
            difficulty INTEGER DEFAULT 3,
            base_person INTEGER DEFAULT 2,
            main_material TEXT DEFAULT '',
            main_weight REAL DEFAULT 0,
            main_unit TEXT DEFAULT 'g',
            is_custom INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS recipe_ingredient (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            material_name TEXT NOT NULL,
            base_amount REAL DEFAULT 0,
            unit TEXT DEFAULT 'g',
            price_per_unit REAL DEFAULT 0,
            single_cost REAL DEFAULT 0,
            is_locked INTEGER DEFAULT 0,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS recipe_step (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            sort_order INTEGER DEFAULT 0,
            content TEXT NOT NULL DEFAULT '',
            image TEXT DEFAULT '',
            FOREIGN KEY (recipe_id) REFERENCES recipe(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS material_category (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS material_library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_name TEXT NOT NULL UNIQUE,
            category_id INTEGER DEFAULT 1,
            default_unit TEXT DEFAULT '斤',
            market_min_price REAL DEFAULT 0,
            market_max_price REAL DEFAULT 0,
            last_user_price REAL DEFAULT 0,
            last_price_date TEXT DEFAULT '',
            history_min REAL DEFAULT 0,
            history_max REAL DEFAULT 0,
            is_custom INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (category_id) REFERENCES material_category(id)
        );

        CREATE TABLE IF NOT EXISTS material_price_record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_id INTEGER NOT NULL,
            price REAL NOT NULL,
            unit TEXT DEFAULT '斤',
            record_date TEXT DEFAULT (date('now','localtime')),
            place TEXT DEFAULT '',
            remark TEXT DEFAULT '',
            FOREIGN KEY (material_id) REFERENCES material_library(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS market_price_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_name TEXT NOT NULL,
            price REAL NOT NULL,
            record_date TEXT DEFAULT (date('now','localtime')),
            city TEXT DEFAULT ''
        );

        CREATE INDEX IF NOT EXISTS idx_recipe_category ON recipe(category);
        CREATE INDEX IF NOT EXISTS idx_recipe_ingredient_recipe ON recipe_ingredient(recipe_id);
        CREATE INDEX IF NOT EXISTS idx_recipe_step_recipe ON recipe_step(recipe_id);
        CREATE INDEX IF NOT EXISTS idx_material_category ON material_library(category_id);
        CREATE INDEX IF NOT EXISTS idx_price_record_material ON material_price_record(material_id);
        CREATE INDEX IF NOT EXISTS idx_price_record_date ON material_price_record(record_date);
        CREATE INDEX IF NOT EXISTS idx_market_price_name ON market_price_data(material_name);
        CREATE INDEX IF NOT EXISTS idx_market_price_date ON market_price_data(record_date);
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == '__main__':
    init_db()
