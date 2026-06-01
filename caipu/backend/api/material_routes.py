"""食材库相关API"""
from flask import Blueprint, request, jsonify
from data.database import get_db_conn

material_bp = Blueprint('material', __name__, url_prefix='/api/material')


def material_to_dict(row):
    return {
        'id': row['id'],
        'material_name': row['material_name'],
        'category_id': row['category_id'],
        'default_unit': row['default_unit'],
        'market_min_price': row['market_min_price'],
        'market_max_price': row['market_max_price'],
        'last_user_price': row['last_user_price'],
        'last_price_date': row['last_price_date'],
        'history_min': row['history_min'],
        'history_max': row['history_max'],
        'is_custom': bool(row['is_custom']),
        'created_at': row['created_at'],
    }


@material_bp.route('/list', methods=['GET'])
def material_list():
    """获取食材库列表，支持搜索和分类"""
    category_id = request.args.get('category_id', '')
    keyword = request.args.get('keyword', '').strip()

    db = get_db_conn()
    conditions = []
    params = []

    if category_id and category_id != '0':
        conditions.append('ml.category_id = ?')
        params.append(int(category_id))
    if keyword:
        conditions.append('ml.material_name LIKE ?')
        params.append(f'%{keyword}%')

    where = ' WHERE ' + ' AND '.join(conditions) if conditions else ''

    sql = f'''
        SELECT ml.*, mc.name as category_name
        FROM material_library ml
        LEFT JOIN material_category mc ON ml.category_id = mc.id
        {where}
        ORDER BY ml.is_custom ASC, ml.material_name ASC
    '''

    rows = db.execute(sql, params).fetchall()
    materials = []
    for r in rows:
        m = material_to_dict(r)
        m['category_name'] = r['category_name'] or ''

        # 获取30天市场均价
        avg_row = db.execute('''
            SELECT AVG(price) as avg_price
            FROM market_price_data
            WHERE material_name = ? AND record_date >= date('now', '-30 days')
        ''', (m['material_name'],)).fetchone()
        m['market_avg_30d'] = round(avg_row['avg_price'], 2) if avg_row['avg_price'] else 0

        # 今日市场价
        today_row = db.execute('''
            SELECT price FROM market_price_data
            WHERE material_name = ? AND record_date = date('now','localtime')
        ''', (m['material_name'],)).fetchone()
        m['market_today'] = round(today_row['price'], 2) if today_row else 0

        # 获取最近一次个人购买记录
        last_record = db.execute('''
            SELECT price, record_date FROM material_price_record
            WHERE material_id = ? ORDER BY record_date DESC LIMIT 1
        ''', (m['id'],)).fetchone()
        if last_record:
            m['last_user_price'] = last_record['price']
            m['last_price_date'] = last_record['record_date']

        materials.append(m)

    db.close()
    return jsonify({'code': 0, 'data': materials})


@material_bp.route('/create', methods=['POST'])
def material_create():
    """新增自定义食材"""
    data = request.json
    db = get_db_conn()
    c = db.cursor()

    # 检查重名
    existing = db.execute(
        'SELECT id FROM material_library WHERE material_name = ?',
        (data['material_name'],)
    ).fetchone()
    if existing:
        db.close()
        return jsonify({'code': 1, 'msg': '该食材已存在'}), 400

    c.execute('''
        INSERT INTO material_library
            (material_name, category_id, default_unit, market_min_price, market_max_price,
             last_user_price, last_price_date, is_custom)
        VALUES (?, ?, ?, ?, ?, ?, date('now','localtime'), 1)
    ''', (
        data['material_name'],
        data.get('category_id', 1),
        data.get('default_unit', '斤'),
        data.get('market_min_price', 0),
        data.get('market_max_price', 0),
        data.get('last_user_price', 0),
    ))
    material_id = c.lastrowid

    # 如果有首次录入价格
    if data.get('last_user_price', 0) > 0:
        c.execute('''
            INSERT INTO material_price_record (material_id, price, unit, record_date, place, remark)
            VALUES (?, ?, ?, date('now','localtime'), ?, ?)
        ''', (
            material_id,
            data['last_user_price'],
            data.get('default_unit', '斤'),
            data.get('place', ''),
            data.get('remark', ''),
        ))

    db.commit()
    db.close()
    return jsonify({'code': 0, 'data': {'id': material_id}, 'msg': '创建成功'})


@material_bp.route('/categories', methods=['GET'])
def material_categories():
    db = get_db_conn()
    rows = db.execute(
        'SELECT * FROM material_category ORDER BY sort_order'
    ).fetchall()
    db.close()
    return jsonify({
        'code': 0,
        'data': [dict(r) for r in rows]
    })
