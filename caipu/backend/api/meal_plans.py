"""点菜规划 API"""
import sys, os, uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from data.database import get_db

meal_plans_bp = Blueprint('meal_plans', __name__)


@meal_plans_bp.route('', methods=['GET'])
def list_plans():
    tenant_id = request.args.get('tenant_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    sql = "SELECT mp.*, r.name as recipe_name FROM meal_plans mp LEFT JOIN recipes r ON mp.recipe_id = r.id WHERE 1=1"
    params = []

    if tenant_id:
        sql += " AND mp.tenant_id = %s"; params.append(tenant_id)
    if start_date:
        sql += " AND mp.plan_date >= %s"; params.append(start_date)
    if end_date:
        sql += " AND mp.plan_date <= %s"; params.append(end_date)

    sql += " ORDER BY mp.plan_date, FIELD(mp.meal_type,'breakfast','lunch','dinner')"

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        return jsonify({"data": cur.fetchall()})


@meal_plans_bp.route('', methods=['POST'])
def upsert_plan():
    """新增单餐（允许同餐段多道菜）"""
    body = request.get_json()
    with get_db() as conn:
        cur = conn.cursor()
        plan_id = f"mp_{uuid.uuid4().hex[:10]}"
        cur.execute(
            "INSERT INTO meal_plans (id, tenant_id, plan_date, meal_type, recipe_id, servings, created_by) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (plan_id, body['tenant_id'], body['plan_date'], body['meal_type'],
             body.get('recipe_id'), body.get('servings', 4), body.get('created_by'))
        )
        # 菜谱做过次数 +1
        if body.get('recipe_id'):
            cur.execute("UPDATE recipes SET cook_count = cook_count + 1 WHERE id = %s", (body['recipe_id'],))
        return jsonify({"id": plan_id, "message": "创建成功"}), 201


@meal_plans_bp.route('/<plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM meal_plans WHERE id = %s", (plan_id,))
        return jsonify({"message": "删除成功"})


@meal_plans_bp.route('/week', methods=['GET'])
def week_plan():
    """获取整周规划（7天 x 3餐）"""
    tenant_id = request.args.get('tenant_id')
    week_start = request.args.get('week_start')

    if not tenant_id or not week_start:
        return jsonify({"error": "tenant_id 和 week_start 必填"}), 400

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT mp.*, r.name as recipe_name FROM meal_plans mp "
            "LEFT JOIN recipes r ON mp.recipe_id = r.id "
            "WHERE mp.tenant_id = %s AND mp.plan_date >= %s AND mp.plan_date < DATE_ADD(%s, INTERVAL 7 DAY) "
            "ORDER BY mp.plan_date, FIELD(mp.meal_type,'breakfast','lunch','dinner')",
            (tenant_id, week_start, week_start)
        )
        return jsonify({"data": cur.fetchall()})
