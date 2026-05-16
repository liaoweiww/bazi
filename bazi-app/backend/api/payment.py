"""
微信小程序支付模块
支持测试模式(本地模拟)和生产模式(真实微信支付API v3)
"""
import json, time, hashlib, hmac, os, uuid
from flask import Blueprint, request, jsonify

payment_bp = Blueprint('payment', __name__)

# ===== 配置 =====
# 改为 True 启用真实支付，需填写下方商户信息
PROD_MODE = False

WECHAT_CONFIG = {
    'appid': 'wx0f0b3f8df2b93bba',       # 小程序AppID
    'mchid': '',                           # 商户号
    'apiv3_key': '',                       # API v3密钥
    'serial_no': '',                       # 证书序列号
    'private_key_path': '',                # 商户私钥.pem路径
    'notify_url': 'https://yourdomain.com/api/payment/callback'
}

# 模拟订单存储（生产环境应使用数据库）
_orders = {}
_purchases = {}  # openid -> 购买记录


def _test_mode_create_order(openid, amount, description):
    """测试模式：模拟下单，返回可直接用的支付参数"""
    order_id = 'TEST' + str(int(time.time() * 1000))
    prepay_id = 'prepay_test_' + order_id
    _orders[order_id] = {
        'order_id': order_id, 'prepay_id': prepay_id,
        'openid': openid, 'amount': amount,
        'description': description, 'paid': False,
        'created_at': time.time()
    }
    return {
        'order_id': order_id,
        'prepay_id': prepay_id,
        'timeStamp': str(int(time.time())),
        'nonceStr': uuid.uuid4().hex[:16],
        'package': 'prepay_id=' + prepay_id,
        'signType': 'RSA',
        'paySign': 'TEST_MODE_SIGNATURE'
    }


def _prod_mode_create_order(openid, amount, description):
    """生产模式：调用微信支付API v3下单"""
    import requests as http_requests

    order_id = 'P' + str(int(time.time() * 1000))

    body = {
        'appid': WECHAT_CONFIG['appid'],
        'mchid': WECHAT_CONFIG['mchid'],
        'description': description,
        'out_trade_no': order_id,
        'notify_url': WECHAT_CONFIG['notify_url'],
        'amount': {
            'total': amount,  # 单位：分
            'currency': 'CNY'
        },
        'payer': {
            'openid': openid
        }
    }

    # 构建签名（简化版，实际需完整实现微信签名算法）
    url = 'https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi'
    try:
        resp = http_requests.post(url, json=body, timeout=10,
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
        if resp.status_code == 200:
            data = resp.json()
            prepay_id = data.get('prepay_id', '')
            return {
                'order_id': order_id,
                'prepay_id': prepay_id,
                'timeStamp': str(int(time.time())),
                'nonceStr': uuid.uuid4().hex[:16],
                'package': 'prepay_id=' + prepay_id,
                'signType': 'RSA',
                'paySign': ''  # 需用商户私钥签名
            }
        else:
            return {'error': resp.text}
    except Exception as e:
        return {'error': str(e)}


# ===== 用户购买状态 =====
def get_user_purchase_status(openid):
    if not openid:
        return {'purchased': False}
    # 检查是否是之前购买过的
    if openid in _purchases:
        return {'purchased': True, 'purchase_time': _purchases[openid]}
    return {'purchased': False}


def mark_user_purchased(openid, order_id):
    _purchases[openid] = {
        'order_id': order_id,
        'purchased_at': time.time(),
        'is_permanent': True
    }


# ===== API路由 =====

@payment_bp.route('/api/payment/create-order', methods=['POST'])
def create_order():
    """创建支付订单"""
    try:
        data = request.get_json() or {}
        openid = data.get('openid', 'test_user_' + uuid.uuid4().hex[:8])
        amount = data.get('amount', 88)  # 单位：分，默认0.88元
        description = data.get('description', '易经八字-解锁完整解读')

        if PROD_MODE:
            result = _prod_mode_create_order(openid, amount, description)
        else:
            result = _test_mode_create_order(openid, amount, description)

        if result.get('error'):
            return jsonify({'success': False, 'error': result['error']}), 500

        return jsonify({'success': True, 'data': result})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    """微信支付回调通知"""
    try:
        data = request.get_json() or {}
        order_id = data.get('out_trade_no', '')

        # 生产模式需验证签名
        if order_id in _orders:
            _orders[order_id]['paid'] = True
            openid = _orders[order_id].get('openid', '')
            if openid:
                mark_user_purchased(openid, order_id)

        return jsonify({'code': 'SUCCESS', 'message': 'OK'})
    except Exception as e:
        return jsonify({'code': 'FAIL', 'message': str(e)}), 500


@payment_bp.route('/api/payment/confirm-test-payment', methods=['POST'])
def confirm_test_payment():
    """测试模式：模拟支付成功（生产环境删除此接口）"""
    if PROD_MODE:
        return jsonify({'success': False, 'error': 'not available in production'}), 403
    try:
        data = request.get_json() or {}
        openid = data.get('openid', '')
        order_id = data.get('order_id', '')

        if order_id in _orders:
            _orders[order_id]['paid'] = True
        if openid:
            mark_user_purchased(openid, order_id)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/api/payment/status', methods=['GET'])
def payment_status():
    """查询用户购买状态"""
    openid = request.args.get('openid', '')
    return jsonify({'success': True, 'data': get_user_purchase_status(openid)})
