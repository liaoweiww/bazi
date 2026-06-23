"""打卡 API"""
import sys, os, uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from data.database import get_db

checkins_bp = Blueprint('checkins', __name__)


@checkins_bp.route('', methods=['POST'])
def checkin():
    """每日打卡（自动计算连续天数）"""
    body = request.get_json()
    user_id = body.get('user_id')
    checkin_date = body.get('checkin_date')

    if not user_id or not checkin_date:
        return jsonify({"error": "user_id 和 checkin_date 必填"}), 400

    with get_db() as conn:
        cur = conn.cursor()
        # 检查今日是否已打卡
        cur.execute("SELECT id FROM checkins WHERE user_id=%s AND checkin_date=%s", (user_id, checkin_date))
        if cur.fetchone():
            return jsonify({"error": "今天已打卡"}), 409

        # 计算连续天数
        cur.execute(
            "SELECT checkin_date FROM checkins WHERE user_id=%s ORDER BY checkin_date DESC LIMIT 1",
            (user_id,))
        last = cur.fetchone()
        streak = 1
        if last:
            from datetime import datetime, timedelta
            last_date = datetime.strptime(str(last['checkin_date']), '%Y-%m-%d')
            today = datetime.strptime(checkin_date, '%Y-%m-%d')
            if (today - last_date).days == 1:
                cur.execute(
                    "SELECT streak_count FROM checkins WHERE user_id=%s ORDER BY checkin_date DESC LIMIT 1",
                    (user_id,))
                last_row = cur.fetchone()
                streak = (last_row['streak_count'] if last_row else 0) + 1

        ck_id = f"ck_{uuid.uuid4().hex[:10]}"
        cur.execute(
            "INSERT INTO checkins (id, user_id, checkin_date, streak_count) VALUES (%s,%s,%s,%s)",
            (ck_id, user_id, checkin_date, streak)
        )
        return jsonify({"id": ck_id, "streak_count": streak, "message": "打卡成功"}), 201


@checkins_bp.route('', methods=['GET'])
def list_checkins():
    user_id = request.args.get('user_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    sql = "SELECT * FROM checkins WHERE 1=1"
    params = []
    if user_id:
        sql += " AND user_id = %s"; params.append(user_id)
    if start_date:
        sql += " AND checkin_date >= %s"; params.append(start_date)
    if end_date:
        sql += " AND checkin_date <= %s"; params.append(end_date)
    sql += " ORDER BY checkin_date DESC"

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        return jsonify({"data": cur.fetchall()})


@checkins_bp.route('/streak', methods=['GET'])
def get_streak():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id 必填"}), 400

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM checkins WHERE user_id=%s ORDER BY checkin_date DESC LIMIT 1", (user_id,))
        last = cur.fetchone()
        return jsonify({"current_streak": last['streak_count'] if last else 0, "last_checkin": last['checkin_date'] if last else None})
