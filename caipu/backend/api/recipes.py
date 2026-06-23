"""菜谱 API（含食材子表 + 步骤子表）"""
import sys, os, uuid, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from data.database import get_db

recipes_bp = Blueprint('recipes', __name__)


@recipes_bp.route('', methods=['GET'])
def list_recipes():
    """菜谱列表（多维度筛选 + 搜索）"""
    tenant_id = request.args.get('tenant_id')
    owner_id = request.args.get('owner_id')
    status = request.args.get('status')
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    meat_type = request.args.get('meat_type')
    search = request.args.get('search')
    is_favorited = request.args.get('is_favorited')
    is_shared = request.args.get('is_shared')

    sql = "SELECT * FROM recipes WHERE 1=1"
    params = []

    if tenant_id:
        sql += " AND tenant_id = %s"; params.append(tenant_id)
    if owner_id:
        sql += " AND owner_id = %s"; params.append(owner_id)
    if status:
        sql += " AND status = %s"; params.append(status)
    if category and category != 'all':
        if category == 'fav':
            sql += " AND is_favorited = 1"
        else:
            sql += " AND category = %s"; params.append(category)
    if difficulty:
        sql += " AND difficulty = %s"; params.append(difficulty)
    if meat_type:
        sql += " AND meat_type = %s"; params.append(meat_type)
    if search:
        sql += " AND (name LIKE %s OR notes LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    if is_favorited:
        sql += " AND is_favorited = %s"; params.append(int(is_favorited))
    if is_shared:
        sql += " AND is_shared = %s"; params.append(int(is_shared))

    sql += " ORDER BY updated_at DESC"

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        return jsonify({"data": rows, "total": len(rows)})


@recipes_bp.route('/<recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """菜谱详情（含食材 + 步骤）"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM recipes WHERE id = %s", (recipe_id,))
        recipe = cur.fetchone()
        if not recipe:
            return jsonify({"error": "菜谱不存在"}), 404

        # 食材列表
        cur.execute(
            "SELECT ri.*, i.name as ingredient_name, i.emoji as ingredient_emoji "
            "FROM recipe_ingredients ri LEFT JOIN ingredients i ON ri.ingredient_id = i.id "
            "WHERE ri.recipe_id = %s ORDER BY ri.sort_order", (recipe_id,))
        recipe['ingredients'] = cur.fetchall()

        # 步骤列表
        cur.execute(
            "SELECT * FROM recipe_steps WHERE recipe_id = %s ORDER BY step_number", (recipe_id,))
        recipe['steps'] = cur.fetchall()

        return jsonify(recipe)


@recipes_bp.route('', methods=['POST'])
def create_recipe():
    """新增菜谱"""
    body = request.get_json()
    if not body or not body.get('name'):
        return jsonify({"error": "菜名必填"}), 400

    recipe_id = f"rec_{uuid.uuid4().hex[:10]}"
    with get_db() as conn:
        cur = conn.cursor()
        ft = body.get('flavor_tags', [])
        flavor_tags = ft if isinstance(ft, str) else json.dumps(ft, ensure_ascii=False)
        cur.execute(
            "INSERT INTO recipes (id, name, image, tenant_id, owner_id, status, category, "
            "difficulty, cook_time, flavor_tags, meat_type, servings, staple_weight, "
            "is_favorited, is_shared, notes, source) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (recipe_id, body['name'], body.get('image', ''), body.get('tenant_id'),
             body.get('owner_id') or None, body.get('status', 'mastered'),
             body.get('category', ''), body.get('difficulty', '3'),
             body.get('cook_time', ''), flavor_tags, body.get('meat_type', 'mix'),
             body.get('servings', 4), body.get('staple_weight'),
             body.get('is_favorited', 0), body.get('is_shared', 0),
             body.get('notes', ''), body.get('source', ''))
        )
        return jsonify({"id": recipe_id, "message": "创建成功"}), 201


@recipes_bp.route('/<recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    body = request.get_json()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM recipes WHERE id = %s", (recipe_id,))
        existing = cur.fetchone()
        if not existing:
            return jsonify({"error": "菜谱不存在"}), 404

        # 只更新请求中实际提供的字段，未提供则保持原值
        ft = body.get('flavor_tags', existing.get('flavor_tags'))
        flavor_tags = ft if isinstance(ft, str) else json.dumps(ft, ensure_ascii=False)
        cur.execute(
            "UPDATE recipes SET name=%s, image=%s, tenant_id=%s, status=%s, category=%s, "
            "difficulty=%s, cook_time=%s, flavor_tags=%s, meat_type=%s, servings=%s, "
            "staple_weight=%s, is_favorited=%s, is_shared=%s, notes=%s, source=%s "
            "WHERE id=%s",
            (body.get('name', existing['name']),
             body.get('image', existing['image']),
             body.get('tenant_id', existing['tenant_id']),
             body.get('status', existing['status']),
             body.get('category', existing['category']),
             body.get('difficulty', existing['difficulty']),
             body.get('cook_time', existing['cook_time']), flavor_tags,
             body.get('meat_type', existing['meat_type']),
             body.get('servings', existing['servings']),
             body.get('staple_weight', existing['staple_weight']),
             body.get('is_favorited', existing['is_favorited']),
             body.get('is_shared', existing['is_shared']),
             body.get('notes', existing['notes']),
             body.get('source', existing['source']),
             recipe_id)
        )
        return jsonify({"message": "更新成功"})


@recipes_bp.route('/<recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM recipe_steps WHERE recipe_id = %s", (recipe_id,))
        cur.execute("DELETE FROM recipe_ingredients WHERE recipe_id = %s", (recipe_id,))
        cur.execute("DELETE FROM meal_plans WHERE recipe_id = %s", (recipe_id,))
        cur.execute("DELETE FROM feast_menu_dishes WHERE recipe_id = %s", (recipe_id,))
        cur.execute("DELETE FROM recipes WHERE id = %s", (recipe_id,))
        return jsonify({"message": "删除成功"})


# ----- 食材子表 -----
@recipes_bp.route('/<recipe_id>/ingredients', methods=['DELETE'])
def clear_ingredients(recipe_id):
    """清空菜谱所有食材（编辑时先删再增）"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM recipe_ingredients WHERE recipe_id = %s", (recipe_id,))
        return jsonify({"message": "已清空"})


@recipes_bp.route('/<recipe_id>/ingredients', methods=['POST'])
def add_ingredient(recipe_id):
    body = request.get_json()
    ing_id = f"ri_{uuid.uuid4().hex[:10]}"
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO recipe_ingredients (id, recipe_id, ingredient_id, amount, unit, is_staple, sort_order) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (ing_id, recipe_id, body['ingredient_id'], body.get('amount', 0),
             body.get('unit', '克'), body.get('is_staple', 0), body.get('sort_order', 0))
        )
        return jsonify({"id": ing_id}), 201


@recipes_bp.route('/<recipe_id>/ingredients/<ing_id>', methods=['PUT'])
def update_ingredient(recipe_id, ing_id):
    body = request.get_json()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE recipe_ingredients SET amount=%s, unit=%s, is_staple=%s, sort_order=%s WHERE id=%s",
            (body.get('amount'), body.get('unit'), body.get('is_staple', 0),
             body.get('sort_order', 0), ing_id)
        )
        return jsonify({"message": "更新成功"})


@recipes_bp.route('/<recipe_id>/ingredients/<ing_id>', methods=['DELETE'])
def delete_ingredient(recipe_id, ing_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM recipe_ingredients WHERE id = %s", (ing_id,))
        return jsonify({"message": "删除成功"})


# ----- 步骤子表 -----
@recipes_bp.route('/<recipe_id>/steps', methods=['DELETE'])
def clear_steps(recipe_id):
    """清空菜谱所有步骤（编辑时先删再增）"""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM recipe_steps WHERE recipe_id = %s", (recipe_id,))
        return jsonify({"message": "已清空"})


@recipes_bp.route('/<recipe_id>/steps', methods=['POST'])
def add_step(recipe_id):
    body = request.get_json()
    step_id = f"rs_{uuid.uuid4().hex[:10]}"
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO recipe_steps (id, recipe_id, step_number, description, image) VALUES (%s,%s,%s,%s,%s)",
            (step_id, recipe_id, body.get('step_number', 1), body.get('description', ''), body.get('image'))
        )
        return jsonify({"id": step_id}), 201


@recipes_bp.route('/<recipe_id>/steps/<step_id>', methods=['PUT'])
def update_step(recipe_id, step_id):
    body = request.get_json()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE recipe_steps SET step_number=%s, description=%s, image=%s WHERE id=%s",
            (body.get('step_number'), body.get('description'), body.get('image'), step_id)
        )
        return jsonify({"message": "更新成功"})


@recipes_bp.route('/<recipe_id>/steps/<step_id>', methods=['DELETE'])
def delete_step(recipe_id, step_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM recipe_steps WHERE id = %s", (step_id,))
        return jsonify({"message": "删除成功"})
