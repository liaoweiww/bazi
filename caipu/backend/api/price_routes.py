"""价格相关API"""
from flask import Blueprint, request, jsonify
from data.database import get_db_conn
from algorithm.price_trend import change_rate, price_level, history_stats, trend_direction

price_bp = Blueprint('price', __name__, url_prefix='/api/price')


@price_bp.route('/record/<int:material_id>', methods=['GET'])
def price_records(material_id):
    """获取某食材的个人价格记录"""
    db = get_db_conn()
    rows = db.execute('''
        SELECT * FROM material_price_record
        WHERE material_id = ?
        ORDER BY record_date DESC
    ''', (material_id,)).fetchall()
    db.close()
    records = [dict(r) for r in rows]
    return jsonify({'code': 0, 'data': records})


@price_bp.route('/record/add', methods=['POST'])
def price_record_add():
    """快速记价"""
    data = request.json
    db = get_db_conn()
    c = db.cursor()

    # 检查食材是否存在
    material = db.execute(
        'SELECT * FROM material_library WHERE id = ?',
        (data['material_id'],)
    ).fetchone()
    if not material:
        db.close()
        return jsonify({'code': 1, 'msg': '食材不存在'}), 404

    price = data['price']
    record_date = data.get('date', '') or 'now'

    c.execute('''
        INSERT INTO material_price_record (material_id, price, unit, record_date, place, remark)
        VALUES (?, ?, ?, date(?), ?, ?)
    ''', (
        data['material_id'],
        price,
        data.get('unit', '斤'),
        record_date,
        data.get('place', ''),
        data.get('remark', ''),
    ))

    # 更新食材库中的最新价格和最低最高价
    all_records = db.execute('''
        SELECT price FROM material_price_record WHERE material_id = ?
    ''', (data['material_id'],)).fetchall()

    prices = [r['price'] for r in all_records]
    c.execute('''
        UPDATE material_library SET
            last_user_price = ?,
            last_price_date = date(?),
            history_min = ?,
            history_max = ?
        WHERE id = ?
    ''', (
        price,
        record_date if record_date != 'now' else 'now',
        min(prices),
        max(prices),
        data['material_id']
    ))

    db.commit()
    db.close()
    return jsonify({'code': 0, 'msg': '记价成功'})


@price_bp.route('/analysis/<int:material_id>', methods=['GET'])
def price_analysis(material_id):
    """价格分析详情（含市场曲线和个人曲线）"""
    db = get_db_conn()

    material = db.execute(
        'SELECT * FROM material_library WHERE id = ?', (material_id,)
    ).fetchone()
    if not material:
        db.close()
        return jsonify({'code': 1, 'msg': '食材不存在'}), 404

    result = dict(material)

    # 30天市场价曲线
    market_rows = db.execute('''
        SELECT record_date, price FROM market_price_data
        WHERE material_name = ? AND record_date >= date('now', '-30 days')
        ORDER BY record_date ASC
    ''', (result['material_name'],)).fetchall()
    result['market_curve'] = [{'date': r['record_date'], 'price': r['price']} for r in market_rows]

    # 个人价格曲线
    personal_rows = db.execute('''
        SELECT record_date, price, place, remark FROM material_price_record
        WHERE material_id = ?
        ORDER BY record_date ASC
    ''', (material_id,)).fetchall()
    result['personal_curve'] = [dict(r) for r in personal_rows]

    # 统计
    stats = history_stats(dict(r) for r in personal_rows)
    result.update(stats)

    # 当前价格档位分析
    today_market = next((p['price'] for p in result['market_curve']
                        if p['date'] == db.execute("SELECT date('now','localtime')").fetchone()[0]), 0)
    if not today_market and result['market_curve']:
        today_market = result['market_curve'][-1]['price']  # 取最近一天

    result['market_today'] = today_market
    result['price_analysis'] = price_level(
        today_market,
        result['market_min_price'],
        result['market_max_price']
    )

    # 涨跌率（与30天均价比较）
    if result['market_curve']:
        avg_30 = round(sum(p['price'] for p in result['market_curve']) / len(result['market_curve']), 2)
        result['change_vs_30d_avg'] = change_rate(avg_30, today_market)

    # 趋势方向
    result['trend'] = trend_direction([dict(r) for r in personal_rows])

    db.close()
    return jsonify({'code': 0, 'data': result})
