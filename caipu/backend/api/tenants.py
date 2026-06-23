"""家庭管理 API"""
import sys, os, uuid, random, string
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
from data.database import get_db

tenants_bp = Blueprint('tenants', __name__)


def _gen_invite_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


@tenants_bp.route('', methods=['POST'])
def create_tenant():
    """创建家庭"""
    body = request.get_json()
    tenant_id = f"t_{uuid.uuid4().hex[:8]}"
    invite_code = _gen_invite_code()

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tenants (id, name, owner_id, invite_code, member_count) VALUES (%s,%s,%s,%s,1)",
            (tenant_id, body['name'], body['owner_id'], invite_code)
        )
        # 户主自动加入
        member_id = f"tm_{uuid.uuid4().hex[:10]}"
        cur.execute(
            "INSERT INTO tenant_members (id, tenant_id, user_id, role) VALUES (%s,%s,%s,'owner')",
            (member_id, tenant_id, body['owner_id'])
        )
        # 更新用户的 home_tenant_id
        cur.execute("UPDATE users SET home_tenant_id = %s WHERE id = %s", (tenant_id, body['owner_id']))
        return jsonify({"id": tenant_id, "invite_code": invite_code}), 201


@tenants_bp.route('/<tenant_id>', methods=['GET'])
def get_tenant(tenant_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tenants WHERE id = %s", (tenant_id,))
        t = cur.fetchone()
        if not t:
            return jsonify({"error": "家庭不存在"}), 404
        return jsonify(t)


@tenants_bp.route('/<tenant_id>', methods=['PUT'])
def update_tenant(tenant_id):
    body = request.get_json()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE tenants SET name=%s WHERE id=%s", (body.get('name'), tenant_id))
        return jsonify({"message": "更新成功"})


@tenants_bp.route('/<tenant_id>/join', methods=['POST'])
def join_tenant(tenant_id):
    """通过邀请码加入"""
    body = request.get_json()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM tenants WHERE id=%s AND invite_code=%s", (body['tenant_id'], body.get('invite_code')))
        t = cur.fetchone()
        if not t:
            return jsonify({"error": "邀请码无效"}), 400

        # 检查是否已是成员
        cur.execute("SELECT id FROM tenant_members WHERE tenant_id=%s AND user_id=%s",
                    (body['tenant_id'], body['user_id']))
        if cur.fetchone():
            return jsonify({"error": "已是成员"}), 409

        member_id = f"tm_{uuid.uuid4().hex[:10]}"
        cur.execute(
            "INSERT INTO tenant_members (id, tenant_id, user_id, role) VALUES (%s,%s,%s,'member')",
            (member_id, body['tenant_id'], body['user_id'])
        )
        cur.execute("UPDATE tenants SET member_count = member_count + 1 WHERE id = %s", (body['tenant_id'],))
        cur.execute("UPDATE users SET home_tenant_id = %s WHERE id = %s", (body['tenant_id'], body['user_id']))
        return jsonify({"message": "加入成功"})


@tenants_bp.route('/<tenant_id>/members', methods=['GET'])
def list_members(tenant_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT tm.*, u.nickname, u.avatar FROM tenant_members tm JOIN users u ON tm.user_id = u.id WHERE tm.tenant_id = %s",
            (tenant_id,))
        return jsonify({"data": cur.fetchall()})


@tenants_bp.route('/<tenant_id>/members/<user_id>', methods=['DELETE'])
def remove_member(tenant_id, user_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM tenant_members WHERE tenant_id=%s AND user_id=%s", (tenant_id, user_id))
        cur.execute("UPDATE tenants SET member_count = member_count - 1 WHERE id = %s", (tenant_id,))
        cur.execute("UPDATE users SET home_tenant_id = NULL WHERE id = %s", (user_id,))
        return jsonify({"message": "移除成功"})


@tenants_bp.route('/<tenant_id>', methods=['DELETE'])
def delete_tenant(tenant_id):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM tenant_members WHERE tenant_id = %s", (tenant_id,))
        cur.execute("DELETE FROM tenants WHERE id = %s", (tenant_id,))
        return jsonify({"message": "家庭已解散"})
