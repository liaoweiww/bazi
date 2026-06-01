"""菜谱相关API"""
from flask import Blueprint, request, jsonify
from data.database import get_db_conn
from algorithm.scale import scale_by_person, scale_by_weight, scale_recipe_ingredients, calc_ingredient_amount
from algorithm.cost import calc_all_ingredient_costs, total_cost, per_person_cost

recipe_bp = Blueprint('recipe', __name__, url_prefix='/api/recipe')


def recipe_row_to_dict(row):
    return {
        'id': row['id'],
        'name': row['name'],
        'cover_image': row['cover_image'],
        'icon_image': row['icon_image'],
        'category': row['category'],
        'cook_time': row['cook_time'],
        'difficulty': row['difficulty'],
        'base_person': row['base_person'],
        'main_material': row['main_material'],
        'main_weight': row['main_weight'],
        'main_unit': row['main_unit'],
        'is_custom': bool(row['is_custom']),
        'created_at': row['created_at'],
        'updated_at': row['updated_at'],
    }


@recipe_bp.route('/list', methods=['GET'])
def recipe_list():
    """获取菜谱列表，支持搜索和分类筛选"""
    category = request.args.get('category', '')
    keyword = request.args.get('keyword', '').strip()

    db = get_db_conn()
    conditions = []
    params = []

    if category and category != '全部':
        conditions.append('category = ?')
        params.append(category)
    if keyword:
        conditions.append("name LIKE ?")
        params.append(f'%{keyword}%')

    where = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
    sql = f'SELECT * FROM recipe{where} ORDER BY is_custom ASC, created_at DESC'

    rows = db.execute(sql, params).fetchall()
    recipes = [recipe_row_to_dict(r) for r in rows]

    # 为每个菜谱计算预估成本
    for recipe in recipes:
        ingredients = db.execute(
            'SELECT * FROM recipe_ingredient WHERE recipe_id = ? ORDER BY sort_order',
            (recipe['id'],)
        ).fetchall()
        ings = []
        for ing in ingredients:
            ings.append({
                'base_amount': ing['base_amount'],
                'unit': ing['unit'],
                'price_per_unit': ing['price_per_unit'],
            })
        ings_with_cost = calc_all_ingredient_costs(ings)
        recipe['estimated_cost'] = total_cost(ings_with_cost)
        recipe['ingredient_count'] = len(ings)

    db.close()
    return jsonify({'code': 0, 'data': recipes})


@recipe_bp.route('/detail/<int:recipe_id>', methods=['GET'])
def recipe_detail(recipe_id):
    """获取菜谱详情（含配料和步骤）"""
    db = get_db_conn()
    recipe = db.execute('SELECT * FROM recipe WHERE id = ?', (recipe_id,)).fetchone()
    if not recipe:
        db.close()
        return jsonify({'code': 1, 'msg': '菜谱不存在'}), 404

    result = recipe_row_to_dict(recipe)

    ingredients = db.execute(
        'SELECT * FROM recipe_ingredient WHERE recipe_id = ? ORDER BY sort_order',
        (recipe_id,)
    ).fetchall()
    result['ingredients'] = [dict(ing) for ing in ingredients]
    result['ingredients'] = calc_all_ingredient_costs(result['ingredients'])
    result['total_cost'] = total_cost(result['ingredients'])
    result['per_person_cost'] = per_person_cost(result['total_cost'], result['base_person'])

    steps = db.execute(
        'SELECT * FROM recipe_step WHERE recipe_id = ? ORDER BY sort_order',
        (recipe_id,)
    ).fetchall()
    result['steps'] = [dict(s) for s in steps]

    db.close()
    return jsonify({'code': 0, 'data': result})


@recipe_bp.route('/create', methods=['POST'])
def recipe_create():
    """新建菜谱"""
    data = request.json
    db = get_db_conn()
    c = db.cursor()

    c.execute('''
        INSERT INTO recipe (name, category, cook_time, difficulty, base_person,
            main_material, main_weight, main_unit, icon_image, cover_image, is_custom)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'], data.get('category', '家常菜'), data.get('cook_time', 30),
        data.get('difficulty', 3), data.get('base_person', 2),
        data.get('main_material', ''), data.get('main_weight', 0),
        data.get('main_unit', 'g'), data.get('icon_image', ''),
        data.get('cover_image', ''), 1
    ))
    recipe_id = c.lastrowid

    # 保存配料
    for i, ing in enumerate(data.get('ingredients', [])):
        c.execute('''
            INSERT INTO recipe_ingredient (recipe_id, material_name, base_amount, unit, price_per_unit, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (recipe_id, ing['material_name'], ing.get('base_amount', 0),
              ing.get('unit', 'g'), ing.get('price_per_unit', 0), i))

    # 保存步骤
    for i, step in enumerate(data.get('steps', [])):
        c.execute('''
            INSERT INTO recipe_step (recipe_id, sort_order, content, image)
            VALUES (?, ?, ?, ?)
        ''', (recipe_id, i + 1, step.get('content', ''), step.get('image', '')))

    db.commit()
    db.close()
    return jsonify({'code': 0, 'data': {'id': recipe_id}, 'msg': '创建成功'})


@recipe_bp.route('/update/<int:recipe_id>', methods=['PUT'])
def recipe_update(recipe_id):
    """编辑菜谱"""
    data = request.json
    db = get_db_conn()
    c = db.cursor()

    existing = db.execute('SELECT id FROM recipe WHERE id = ?', (recipe_id,)).fetchone()
    if not existing:
        db.close()
        return jsonify({'code': 1, 'msg': '菜谱不存在'}), 404

    c.execute('''
        UPDATE recipe SET name=?, category=?, cook_time=?, difficulty=?, base_person=?,
            main_material=?, main_weight=?, main_unit=?, icon_image=?, cover_image=?,
            updated_at=datetime('now','localtime')
        WHERE id=?
    ''', (
        data['name'], data.get('category', '家常菜'), data.get('cook_time', 30),
        data.get('difficulty', 3), data.get('base_person', 2),
        data.get('main_material', ''), data.get('main_weight', 0),
        data.get('main_unit', 'g'), data.get('icon_image', ''),
        data.get('cover_image', ''), recipe_id
    ))

    # 重建配料
    c.execute('DELETE FROM recipe_ingredient WHERE recipe_id = ?', (recipe_id,))
    for i, ing in enumerate(data.get('ingredients', [])):
        c.execute('''
            INSERT INTO recipe_ingredient (recipe_id, material_name, base_amount, unit, price_per_unit, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (recipe_id, ing['material_name'], ing.get('base_amount', 0),
              ing.get('unit', 'g'), ing.get('price_per_unit', 0), i))

    # 重建步骤
    c.execute('DELETE FROM recipe_step WHERE recipe_id = ?', (recipe_id,))
    for i, step in enumerate(data.get('steps', [])):
        c.execute('''
            INSERT INTO recipe_step (recipe_id, sort_order, content, image)
            VALUES (?, ?, ?, ?)
        ''', (recipe_id, i + 1, step.get('content', ''), step.get('image', '')))

    db.commit()
    db.close()
    return jsonify({'code': 0, 'msg': '更新成功'})


@recipe_bp.route('/delete/<int:recipe_id>', methods=['DELETE'])
def recipe_delete(recipe_id):
    """删除菜谱"""
    db = get_db_conn()
    db.execute('DELETE FROM recipe WHERE id = ?', (recipe_id,))
    db.commit()
    db.close()
    return jsonify({'code': 0, 'msg': '删除成功'})


@recipe_bp.route('/<int:recipe_id>/scale', methods=['POST'])
def recipe_scale(recipe_id):
    """
    双模式换算
    mode=A: 按人头换算 {mode:'person', target_person: 4}
    mode=B: 按主料重量换算 {mode:'weight', target_weight: 750}
    """
    data = request.json
    mode = data.get('mode', 'person')
    locked_ids = set(data.get('locked_ids', []))

    db = get_db_conn()
    recipe = db.execute('SELECT * FROM recipe WHERE id = ?', (recipe_id,)).fetchone()
    if not recipe:
        db.close()
        return jsonify({'code': 1, 'msg': '菜谱不存在'}), 404

    if mode == 'person':
        target = data.get('target_person', recipe['base_person'])
        scale = scale_by_person(recipe['base_person'], target)
        estimated_people = target
    else:
        target = data.get('target_weight', recipe['main_weight'])
        scale = scale_by_weight(recipe['main_weight'], target)
        estimated_people = round(recipe['base_person'] * scale, 1)

    ingredients = db.execute(
        'SELECT * FROM recipe_ingredient WHERE recipe_id = ? ORDER BY sort_order',
        (recipe_id,)
    ).fetchall()

    scaled_ings = []
    for ing in ingredients:
        item = dict(ing)
        if ing['id'] in locked_ids:
            item['is_locked'] = 1
            item['scaled_amount'] = item['base_amount']
        else:
            item['is_locked'] = 0
            item['scaled_amount'] = calc_ingredient_amount(item['base_amount'], scale)
        scaled_ings.append(item)

    scaled_ings = calc_all_ingredient_costs(scaled_ings)
    t_cost = total_cost(scaled_ings)

    db.close()
    return jsonify({
        'code': 0,
        'data': {
            'scale': round(scale, 3),
            'mode': mode,
            'estimated_people': estimated_people,
            'ingredients': scaled_ings,
            'total_cost': t_cost,
            'per_person_cost': per_person_cost(t_cost, estimated_people)
        }
    })


@recipe_bp.route('/categories', methods=['GET'])
def recipe_categories():
    return jsonify({
        'code': 0,
        'data': ['全部', '家常菜', '快手菜', '汤品', '荤菜', '素菜']
    })
