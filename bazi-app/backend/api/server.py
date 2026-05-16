"""
易经八字APP - API服务层
Flask REST API，提供排盘、解读等接口
"""
import sys
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# 确保backend目录在路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)


def get_paipan_function():
    """延迟导入排盘函数"""
    from algorithm.paipan import paipan
    return paipan


def get_text_engine():
    """延迟导入文案引擎"""
    from texts.engine import TextEngine
    return TextEngine()


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "app": "易经八字推算系统",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/calendar/lunar-to-solar', methods=['POST'])
def api_lunar_to_solar():
    """农历转公历接口"""
    try:
        data = request.get_json()
        from lunarcal.lunar_solar import lunar_to_solar
        result = lunar_to_solar(
            year=int(data['year']),
            month=int(data['month']),
            day=int(data['day']),
            leap=bool(data.get('leap', False))
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/vernacular', methods=['POST'])
def api_vernacular():
    """白话解读接口"""
    try:
        data = request.get_json()
        paipan_result = data.get('paipan_result', {})
        from texts.vernacular import generate_vernacular
        result = generate_vernacular(paipan_result)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/paipan', methods=['POST'])
def api_paipan():
    """
    八字排盘接口

    请求参数:
    {
        "name": "张三",
        "gender": "男",
        "solar_year": 1990,
        "solar_month": 6,
        "solar_day": 15,
        "hour": 8,
        "minute": 30,
        "longitude": 116.4,
        "latitude": 39.9
    }
    """
    try:
        data = request.get_json()

        required = ['gender', 'hour']
        for field in required:
            if field not in data:
                return jsonify({"error": f"缺少必要参数: {field}"}), 400

        gender = data.get('gender', '男')
        hour = int(data.get('hour', 0))
        minute = int(data.get('minute', 0))
        longitude = float(data.get('longitude', 120.0))
        latitude = float(data.get('latitude', 30.0))
        name = data.get('name', '')

        # 支持农历输入
        if data.get('calendar_type') == 'lunar':
            from lunarcal.lunar_solar import lunar_to_solar
            lunar_year = int(data.get('lunar_year', 0))
            lunar_month = int(data.get('lunar_month', 0))
            lunar_day = int(data.get('lunar_day', 0))
            leap = bool(data.get('leap_month', False))
            if not lunar_year or not lunar_month or not lunar_day:
                return jsonify({"error": "农历日期参数不完整"}), 400
            solar = lunar_to_solar(lunar_year, lunar_month, lunar_day, leap)
            solar_year = solar['year']
            solar_month = solar['month']
            solar_day = solar['day']
        else:
            solar_year = int(data.get('solar_year', 0))
            solar_month = int(data.get('solar_month', 0))
            solar_day = int(data.get('solar_day', 0))

        if not solar_year or not solar_month or not solar_day:
            return jsonify({"error": "日期参数不完整"}), 400

        # 调用排盘算法
        paipan = get_paipan_function()
        result = paipan(
            solar_year=solar_year,
            solar_month=solar_month,
            solar_day=solar_day,
            hour=hour,
            minute=minute,
            longitude=longitude,
            latitude=latitude,
            gender=gender
        )

        # 添加请求元信息
        result['name'] = name
        result['request_time'] = datetime.now().isoformat()

        return jsonify({
            "success": True,
            "data": result
        })

    except ValueError as e:
        return jsonify({"error": f"参数格式错误: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"排盘失败: {str(e)}"}), 500


@app.route('/api/interpret', methods=['POST'])
def api_interpret():
    """
    文案解读接口

    请求参数: 排盘结果JSON
    返回: 各维度专业解读
    """
    try:
        data = request.get_json()
        paipan_result = data.get('paipan_result', {})

        if not paipan_result:
            return jsonify({"error": "缺少排盘结果"}), 400

        engine = get_text_engine()
        interpretation = engine.interpret(paipan_result)

        return jsonify({
            "success": True,
            "data": interpretation
        })

    except Exception as e:
        return jsonify({"error": f"解读失败: {str(e)}"}), 500


@app.route('/api/calendar/solar-to-lunar', methods=['POST'])
def api_solar_to_lunar():
    """公历转农历接口"""
    try:
        data = request.get_json()
        from lunarcal.lunar_solar import solar_to_lunar

        result = solar_to_lunar(
            year=int(data['year']),
            month=int(data['month']),
            day=int(data['day'])
        )

        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/calendar/solar-terms', methods=['GET'])
def api_solar_terms():
    """获取指定年份节气列表"""
    try:
        year = int(request.args.get('year', datetime.now().year))
        from lunarcal.solar_terms import get_all_solar_terms

        terms = get_all_solar_terms(year)
        return jsonify({"success": True, "data": terms})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/data/tiangan', methods=['GET'])
def api_tiangan():
    """获取天干列表"""
    from data.queries import get_all_tiangan
    result = get_all_tiangan()
    return jsonify({"success": True, "data": result})


@app.route('/api/data/dizhi', methods=['GET'])
def api_dizhi():
    """获取地支列表"""
    from data.queries import get_all_dizhi
    result = get_all_dizhi()
    return jsonify({"success": True, "data": result})


@app.route('/api/data/shishen/<ri_gan>/<other_gan>', methods=['GET'])
def api_shishen(ri_gan, other_gan):
    """查询十神关系"""
    from data.queries import get_shishen
    result = get_shishen(ri_gan, other_gan)
    return jsonify({"success": True, "data": result})


@app.route('/')
def index():
    """返回网页预览页面"""
    import os as _os
    template_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'templates')
    return send_from_directory(template_dir, 'preview.html')


@app.route('/manifest.json')
def pwa_manifest():
    import os as _os
    template_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'templates')
    return send_from_directory(template_dir, 'manifest.json', mimetype='application/manifest+json')


@app.route('/sw.js')
def pwa_sw():
    import os as _os
    template_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'templates')
    return send_from_directory(template_dir, 'sw.js', mimetype='application/javascript')


@app.route('/icon-<int:size>.png')
def pwa_icon(size):
    import os as _os
    template_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'templates')
    return send_from_directory(template_dir, f'icon-{size}.png')


@app.route('/api/year-fortune', methods=['POST'])
def api_year_fortune():
    """年运分析接口"""
    try:
        data = request.get_json()
        paipan_result = data.get('paipan_result', {})
        target_year = data.get('year', None)
        if not paipan_result:
            return jsonify({"error": "缺少排盘结果"}), 400
        from texts.extended import generate_year_fortune
        result = generate_year_fortune(paipan_result, target_year)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"error": f"年运分析失败: {str(e)}"}), 500


@app.route('/api/current-fortune', methods=['POST'])
def api_current_fortune():
    """当前时运分析接口"""
    try:
        data = request.get_json()
        paipan_result = data.get('paipan_result', {})
        if not paipan_result:
            return jsonify({"error": "缺少排盘结果"}), 400
        from texts.extended import generate_current_fortune
        result = generate_current_fortune(paipan_result)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"error": f"时运分析失败: {str(e)}"}), 500


@app.route('/api/remedy', methods=['POST'])
def api_remedy():
    """破解法接口"""
    try:
        data = request.get_json()
        paipan_result = data.get('paipan_result', {})
        if not paipan_result:
            return jsonify({"error": "缺少排盘结果"}), 400
        from texts.extended import generate_remedy
        result = generate_remedy(paipan_result)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"error": f"破解法分析失败: {str(e)}"}), 500


@app.route('/api/control-guide', methods=['GET'])
def api_control_guide():
    """人生把控指南接口"""
    try:
        from texts.extended import CONTROL_GUIDE
        return jsonify({"success": True, "data": CONTROL_GUIDE})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/reference-books', methods=['GET'])
def api_reference_books():
    """参考书籍接口"""
    try:
        from texts.extended import REFERENCE_BOOKS
        return jsonify({"success": True, "data": REFERENCE_BOOKS})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/life-summary', methods=['POST'])
def api_life_summary():
    """四大运势白话总结接口"""
    try:
        data = request.get_json()
        paipan_result = data.get('paipan_result', {})
        if not paipan_result:
            return jsonify({"error": "缺少排盘结果"}), 400
        from texts.extended import generate_life_summary
        result = generate_life_summary(paipan_result)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/calendar/today', methods=['GET'])
def api_calendar_today():
    """今日农历信息"""
    try:
        today = datetime.now()
        from lunarcal.lunar_solar import solar_to_lunar, get_lunar_year_info, get_ganzhi_day, get_ganzhi_year
        lunar = solar_to_lunar(today.year, today.month, today.day)
        ganzhi_day = get_ganzhi_day(today)
        ganzhi_year = get_ganzhi_year(today.year)
        year_info = get_lunar_year_info(today.year)

        # 今日节气（简单判断，近似的）
        solar_term = lunar.get('solar_term', '') if isinstance(lunar, dict) else ''

        return jsonify({"success": True, "data": {
            "solar_date": today.strftime("%Y-%m-%d"),
            "lunar_year": lunar.get('lunar_year', today.year) if isinstance(lunar, dict) else today.year,
            "lunar_month": lunar.get('lunar_month', today.month) if isinstance(lunar, dict) else today.month,
            "lunar_day": lunar.get('lunar_day', today.day) if isinstance(lunar, dict) else today.day,
            "lunar_month_name": lunar.get('lunar_month_name', '') if isinstance(lunar, dict) else '',
            "lunar_day_name": lunar.get('lunar_day_name', '') if isinstance(lunar, dict) else '',
            "is_leap_month": lunar.get('is_leap', False) if isinstance(lunar, dict) else False,
            "ganzhi_day": ganzhi_day or '',
            "ganzhi_year": ganzhi_year or '',
            "zodiac": year_info.get('zodiac', '') if isinstance(year_info, dict) else '',
            "solar_term": solar_term,
            "weekday": ['日', '一', '二', '三', '四', '五', '六'][today.weekday()]
        }})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/daily-fortune', methods=['POST'])
def api_daily_fortune():
    """每日运势简要"""
    try:
        data = request.get_json()
        paipan_result = data.get('paipan_result', {})
        if not paipan_result:
            return jsonify({"error": "缺少排盘结果"}), 400

        today = datetime.now()
        from lunarcal.lunar_solar import get_ganzhi_day
        day_ganzhi = get_ganzhi_day(today)
        day_gan = day_ganzhi[0] if day_ganzhi else '甲'
        day_zhi = day_ganzhi[1] if day_ganzhi else '子'

        # 获取日主
        dm_gan = paipan_result.get('day_master', '')

        # 天干五行映射
        gan_wx = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
                   '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
        # 天干十神关系（日主 vs 其他天干）
        gan_order = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        shishen_map = ['比肩', '劫财', '食神', '伤官', '偏财', '正财', '七杀', '正官', '偏印', '正印']

        dm_idx = gan_order.index(dm_gan) if dm_gan in gan_order else 0
        day_idx = gan_order.index(day_gan) if day_gan in gan_order else 0
        diff = (day_idx - dm_idx) % 10
        relation = shishen_map[diff] if diff < len(shishen_map) else '比肩'

        # 五行生克评分
        day_wx = gan_wx.get(day_gan, '土')
        dm_wx = gan_wx.get(dm_gan, '土')
        wx_cycle = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        wx_ke = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}

        score = 60
        tips = []
        if wx_cycle.get(dm_wx) == day_wx:
            score = 80; tips.append(f"今日{day_wx}气生你日主{dm_wx}，精力充沛，适合主动出击")
        elif wx_cycle.get(day_wx) == dm_wx:
            score = 75; tips.append(f"你日主{dm_wx}生今日{day_wx}气，宜分享付出，不宜强求")
        elif dm_wx == day_wx:
            score = 70; tips.append(f"今日与日主同为{dm_wx}气，平稳顺遂，宜守不宜攻")
        elif wx_ke.get(day_wx) == dm_wx:
            score = 45; tips.append(f"今日{day_wx}气克你日主{dm_wx}，阻力较大，宜低调谨慎")
        elif wx_ke.get(dm_wx) == day_wx:
            score = 65; tips.append(f"你日主{dm_wx}克今日{day_wx}气，需付出努力，劳有所得")

        rating = '大吉' if score >= 80 else '小吉' if score >= 70 else '平平' if score >= 55 else '欠佳'

        # 宜忌简要
        yi = []
        ji = []
        if score >= 70:
            yi = ['签约', '出行', '会友']
            ji = ['争执', '诉讼']
        elif score >= 55:
            yi = ['学习', '规划', '静养']
            ji = ['重大投资', '远行']
        else:
            yi = ['反省', '整理', '低调行事']
            ji = ['冒险', '大额支出', '重要决策']

        return jsonify({"success": True, "data": {
            "date": today.strftime("%Y-%m-%d"),
            "day_ganzhi": day_ganzhi,
            "day_wuxing": day_wx,
            "relation_to_dm": relation,
            "score": score,
            "rating": rating,
            "tips": tips,
            "yi": yi,
            "ji": ji,
            "weekday": ['日', '一', '二', '三', '四', '五', '六'][today.weekday()]
        }})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("=" * 50)
    print("  易经八字推算系统 API Server")
    print("  运行地址: http://localhost:5000")
    print("  健康检查: http://localhost:5000/api/health")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
