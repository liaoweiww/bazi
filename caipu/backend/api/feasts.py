"""宴席菜单 API"""
import sys, os, uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from data.database import get_db

feasts_bp = Blueprint('feasts', __name__)

# 内置场景模板
TEMPLATES = [
    {"type": "casual", "name": "家常小聚", "servings": 4, "structure": {"cold": 2, "hot_meat": 3, "hot_veg": 1, "soup": 1, "staple": 0, "dessert": 0}},
    {"type": "couple", "name": "双人简餐", "servings": 2, "structure": {"cold": 1, "hot_meat": 2, "hot_veg": 1, "soup": 1, "staple": 0, "dessert": 0}},
    {"type": "friends", "name": "朋友聚餐", "servings": 6, "structure": {"cold": 3, "hot_meat": 5, "hot_veg": 2, "soup": 1, "staple": 0, "dessert": 1}},
    {"type": "elders", "name": "长辈宴请", "servings": 8, "structure": {"cold": 4, "hot_meat": 6, "hot_veg": 3, "soup": 2, "staple": 0, "dessert": 1}},
    {"type": "holiday", "name": "节日正餐", "servings": 10, "structure": {"cold": 4, "hot_meat": 8, "hot_veg": 4, "soup": 2, "staple": 0, "dessert": 2}},
    {"type": "newyear", "name": "年夜饭", "servings": 12, "structure": {"cold": 6, "hot_meat": 10, "hot_veg": 4, "soup": 3, "staple": 0, "dessert": 2}},
]


@feasts_bp.route('/templates', methods=['GET'])
def get_templates():
    return jsonify(TEMPLATES)


@feasts_bp.route('', methods=['GET'])
def list_feasts():
    tenant_id = request.args.get('tenant_id')
    sql = "SELECT * FROM feast_menus WHERE 1=1"
    params = []
    if tenant_id:
        sql += " AND tenant_id = %s"; params.append(tenant_id)
    sql += " ORDER BY created_at DESC"

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        return jsonify({"data": cur.fetchall()})


@feasts_bp.route('', methods=['POST'])
def create_feast():
    body = request.get_json()
    menu_id = f"fm_{uuid.uuid4().hex[:10]}"
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO feast_menus (id, tenant_id, name, template_type, scene, servings, event_date, created_by) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (menu_id, body.get('tenant_id'), body['name'], body.get('template_type'),
             body.get('scene'), body.get('servings', 6), body.get('event_date'), body.get('created_by'))
        )
        return jsonify({"id": menu_id, "message": "创建成功"}), 201


@feasts_bp.route('/<menu_id>', methods=['GET'])
def get_feast(menu_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM feast_menus WHERE id = %s", (menu_id,))
        menu = cur.fetchone()
        if not menu:
            return jsonify({"error": "宴席不存在"}), 404

        cur.execute(
            "SELECT fd.*, r.name as recipe_name, r.emoji FROM feast_menu_dishes fd "
            "LEFT JOIN recipes r ON fd.recipe_id = r.id WHERE fd.menu_id = %s ORDER BY fd.sort_order", (menu_id,))
        menu['dishes'] = cur.fetchall()
        return jsonify(menu)


@feasts_bp.route('/<menu_id>', methods=['PUT'])
def update_feast(menu_id):
    body = request.get_json()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE feast_menus SET name=%s, servings=%s, event_date=%s, scene=%s WHERE id=%s",
            (body.get('name'), body.get('servings', 6), body.get('event_date'), body.get('scene'), menu_id)
        )
        return jsonify({"message": "更新成功"})


@feasts_bp.route('/<menu_id>', methods=['DELETE'])
def delete_feast(menu_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM feast_menu_dishes WHERE menu_id = %s", (menu_id,))
        cur.execute("DELETE FROM feast_menus WHERE id = %s", (menu_id,))
        return jsonify({"message": "删除成功"})


@feasts_bp.route('/<menu_id>/dishes', methods=['POST'])
def add_dish(menu_id):
    body = request.get_json()
    dish_id = f"fd_{uuid.uuid4().hex[:10]}"
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO feast_menu_dishes (id, menu_id, recipe_id, feast_category, sort_order) VALUES (%s,%s,%s,%s,%s)",
            (dish_id, menu_id, body['recipe_id'], body.get('feast_category', 'hot_meat'), body.get('sort_order', 0))
        )
        return jsonify({"id": dish_id}), 201


@feasts_bp.route('/<menu_id>/dishes/<dish_id>', methods=['DELETE'])
def remove_dish(menu_id, dish_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM feast_menu_dishes WHERE id = %s", (dish_id,))
        return jsonify({"message": "删除成功"})
