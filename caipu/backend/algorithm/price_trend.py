"""价格曲线、涨跌、档位分析算法"""


def change_rate(old_price, new_price):
    """涨跌幅度(%)"""
    if old_price <= 0:
        return 0
    return round((new_price - old_price) / old_price * 100, 1)


def price_level(current, min_p, max_p):
    """价格档位判断"""
    if min_p <= 0 or max_p <= 0:
        return '无参考数据'
    mid = (min_p + max_p) / 2
    if current <= mid * 0.9:
        return '偏低，适合购入'
    elif current >= mid * 1.1:
        return '偏高，不建议购入'
    else:
        return '适中'


def history_stats(records):
    """历史价格统计：最高/最低/均价"""
    if not records:
        return {'min': 0, 'max': 0, 'avg': 0, 'count': 0}
    prices = [r['price'] for r in records]
    return {
        'min': round(min(prices), 2),
        'max': round(max(prices), 2),
        'avg': round(sum(prices) / len(prices), 2),
        'count': len(prices)
    }


def trend_direction(records):
    """趋势方向：涨/跌/稳"""
    if len(records) < 2:
        return '数据不足'
    recent = records[-3:] if len(records) >= 3 else records[-2:]
    prices = [r['price'] for r in recent]
    if all(prices[i] < prices[i + 1] for i in range(len(prices) - 1)):
        return '↑ 持续上涨'
    elif all(prices[i] > prices[i + 1] for i in range(len(prices) - 1)):
        return '↓ 持续下跌'
    else:
        return '→ 价格平稳'
