"""双模式智能换算算法"""


def scale_by_person(base_person, target_person):
    """按人头换算倍率"""
    if base_person <= 0:
        return 1.0
    return target_person / base_person


def scale_by_weight(base_weight, target_weight):
    """按主料重量换算倍率"""
    if base_weight <= 0:
        return 1.0
    return target_weight / base_weight


def calc_ingredient_amount(base_amount, scale):
    """计算单项配料换算后用量"""
    return round(base_amount * scale, 2)


def estimate_people(base_person, scale):
    """反推预估人数"""
    return round(base_person * scale, 1)


def scale_recipe_ingredients(ingredients, scale):
    """批量换算所有配料（跳过锁定项）"""
    result = []
    for ing in ingredients:
        item = dict(ing)
        if not item.get('is_locked'):
            item['scaled_amount'] = calc_ingredient_amount(item['base_amount'], scale)
        else:
            item['scaled_amount'] = item['base_amount']
        result.append(item)
    return result
