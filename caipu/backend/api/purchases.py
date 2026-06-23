"""采购记录 API"""
import sys, os, uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from data.database import get_db

purchases_bp = Blueprint('purchases', __name__)


@purchases_bp.route('', methods=['GET'])
def list_purchases():
    tenant_id = request.args.get('tenant_id')
    ingredient_id = request.args.get('ingredient_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    location = request.args.get('location')

    sql = "SELECT p.*, i.name as ingredient_name, i.emoji as ingredient_emoji, i.category1, i.category2 FROM purchases p LEFT JOIN ingredients i ON p.ingredient_id = i.id WHERE 1=1"
    params = []

    if tenant_id:
        sql += " AND p.tenant_id = %s"; params.append(tenant_id)
    if ingredient_id:
        sql += " AND p.ingredient_id = %s"; params.append(ingredient_id)
    if start_date:
        sql += " AND p.purchase_date >= %s"; params.append(start_date)
    if end_date:
        sql += " AND p.purchase_date <= %s"; params.append(end_date)
    if location:
        sql += " AND p.location = %s"; params.append(location)

    sql += " ORDER BY p.purchase_date DESC, p.created_at DESC"

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        return jsonify({"data": cur.fetchall()})


@purchases_bp.route('', methods=['POST'])
def create_purchase():
    body = request.get_json()
    pur_id = f"pur_{uuid.uuid4().hex[:10]}"
    # 优先使用前端传来的 total_price（已正确换算克/斤），否则后端算
    qty = body.get('quantity', 1)
    total_price = body.get('total_price') or round(body.get('price', 0) * qty / 500, 2)
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO purchases (id, tenant_id, ingredient_id, price, total_price, quantity, unit, purchase_date, location, note, created_by) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (pur_id, body.get('tenant_id'), body['ingredient_id'], body['price'],
             total_price, qty, body.get('unit', 'g'),
             body.get('purchase_date'), body.get('location', ''), body.get('note', ''),
             body.get('created_by'))
        )
        return jsonify({"id": pur_id, "message": "录入成功"}), 201


@purchases_bp.route('/<purchase_id>', methods=['PUT'])
def update_purchase(purchase_id):
    body = request.get_json()
    qty = body.get('quantity', 1)
    total_price = body.get('total_price') or round(body.get('price', 0) * qty / 500, 2)
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE purchases SET price=%s, total_price=%s, quantity=%s, unit=%s, purchase_date=%s, location=%s, note=%s WHERE id=%s",
            (body.get('price'), total_price, qty, body.get('unit', 'g'),
             body.get('purchase_date'), body.get('location'), body.get('note'), purchase_id)
        )
        return jsonify({"message": "更新成功"})


@purchases_bp.route('/<purchase_id>', methods=['DELETE'])
def delete_purchase(purchase_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM purchases WHERE id = %s", (purchase_id,))
        return jsonify({"message": "删除成功"})


@purchases_bp.route('/stats', methods=['GET'])
def purchase_stats():
    """采购统计"""
    tenant_id = request.args.get('tenant_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    with get_db() as conn:
        cur = conn.cursor()
        # 总支出
        cur.execute(
            "SELECT COALESCE(SUM(total_price), 0) as total FROM purchases WHERE tenant_id=%s AND purchase_date BETWEEN %s AND %s",
            (tenant_id, start_date, end_date))
        total = cur.fetchone()['total']

        # 按分类统计
        cur.execute(
            "SELECT i.category1, COALESCE(SUM(p.total_price),0) as subtotal "
            "FROM purchases p JOIN ingredients i ON p.ingredient_id = i.id "
            "WHERE p.tenant_id=%s AND p.purchase_date BETWEEN %s AND %s "
            "GROUP BY i.category1 ORDER BY subtotal DESC",
            (tenant_id, start_date, end_date))
        by_category = cur.fetchall()

        # 采购次数
        cur.execute(
            "SELECT COUNT(*) as cnt FROM purchases WHERE tenant_id=%s AND purchase_date BETWEEN %s AND %s",
            (tenant_id, start_date, end_date))
        count = cur.fetchone()['cnt']

        return jsonify({
            "total_spend": float(total),
            "purchase_count": count,
            "by_category": by_category
        })
