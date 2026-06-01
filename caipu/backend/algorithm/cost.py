"""菜谱精准成本核算算法"""
from .unit_convert import to_gram, gram_to_jin


def single_ingredient_cost(amount, unit, price_per_jin):
    """单项配料成本 = 用量(转斤) × 单价(元/斤)"""
    gram = to_gram(amount, unit)
    jin = gram_to_jin(gram)
    return round(jin * price_per_jin, 2)


def total_cost(ingredients):
    """总成本汇总"""
    return round(sum(ing.get('single_cost', 0) for ing in ingredients), 2)


def per_person_cost(total, people):
    """人均成本"""
    if people <= 0:
        return 0
    return round(total / people, 2)


def calc_all_ingredient_costs(ingredients):
    """计算所有配料成本并返回更新后的列表"""
    result = []
    for ing in ingredients:
        item = dict(ing)
        amount = item.get('scaled_amount', item.get('base_amount', 0))
        unit = item.get('unit', 'g')
        price = item.get('price_per_unit', 0)
        item['single_cost'] = single_ingredient_cost(amount, unit, price)
        result.append(item)
    return result
