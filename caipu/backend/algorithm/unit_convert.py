"""多单位自动换算算法"""

# 基础换算常量
JIN_TO_GRAM = 500      # 1斤 = 500g
LIANG_TO_GRAM = 50     # 1两 = 50g
SPOON_TO_ML = 15       # 1标准勺 = 15ml
TEASPOON_TO_ML = 5     # 1小勺 = 5ml


def to_gram(value, unit):
    """任意单位 → 克"""
    u = (unit or '').strip().lower()
    if u in ('g', '克', 'gram'):
        return value
    if u in ('斤', 'jin'):
        return value * JIN_TO_GRAM
    if u in ('两', 'liang'):
        return value * LIANG_TO_GRAM
    if u in ('kg', '千克', '公斤'):
        return value * 1000
    if u in ('个', '只', '条', '根', '块'):
        return value  # 不可换算，保持原值
    return value


def from_gram(value, target_unit):
    """克 → 目标单位"""
    u = (target_unit or '').strip().lower()
    if u in ('g', '克', 'gram'):
        return value
    if u in ('斤', 'jin'):
        return value / JIN_TO_GRAM
    if u in ('两', 'liang'):
        return value / LIANG_TO_GRAM
    if u in ('kg', '千克', '公斤'):
        return value / 1000
    return value


def to_ml(value, unit):
    """任意单位 → ml"""
    u = (unit or '').strip().lower()
    if u in ('ml', '毫升'):
        return value
    if u in ('勺', '大勺', '汤匙'):
        return value * SPOON_TO_ML
    if u in ('小勺', '茶匙', 'tsp'):
        return value * TEASPOON_TO_ML
    if u in ('l', '升'):
        return value * 1000
    return value


def jin_to_gram(val):
    return val * JIN_TO_GRAM


def gram_to_jin(val):
    return val / JIN_TO_GRAM


def liang_to_gram(val):
    return val * LIANG_TO_GRAM


def spoon_to_ml(val):
    return val * SPOON_TO_ML


UNIT_DISPLAY = {
    'g': '克', '斤': '斤', '两': '两', 'kg': '千克',
    'ml': '毫升', '勺': '大勺', '小勺': '小勺', 'l': '升',
    '个': '个', '只': '只', '条': '条', '根': '根', '块': '块'
}
