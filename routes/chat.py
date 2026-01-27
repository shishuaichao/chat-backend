
from flask import Blueprint, jsonify, request
from wechat.operate import get_all_chats
from db_config import get_db

# 1. 创建蓝图（参数：蓝图名、模块名、URL前缀）
chat_bp = Blueprint(
    "wechat",          # 蓝图唯一标识
    __name__,          # 当前模块名
    url_prefix="/chat"  # 该蓝图下所有路由的统一前缀（可选，简化路由）
)

# 2. 创建会话（私聊/群聊）
@chat_bp.route('/conversation/create', methods=['POST'])
def create_conv():
    data = request.json
    type_ = data['type']  # 1=私聊 2=群聊
    name = data.get('name', '')
    owner_id = data['owner_id']
    member_ids = data['member_ids']  # 成员ID列表
    db = get_db()
    with db.cursor() as cur:
        # 插入会话
        cur.execute(
            "INSERT INTO conversations (type, name, owner_id) VALUES (%s, %s, %s)",
            (type_, name, owner_id)
        )
        conv_id = cur.lastrowid
        # 插入成员
        for user_id in member_ids:
            cur.execute(
                "INSERT INTO conversation_members (conversation_id, user_id) VALUES (%s, %s)",
                (conv_id, user_id)
            )
        db.commit()
    return jsonify({"code": 200, "data": {"conv_id": conv_id}, "msg": "创建成功"})

# 2. 用蓝图装饰器定义路由（替代原有的@app.route）
@chat_bp.route('/records', methods=['GET'])
def get_chats():
    res = get_all_chats()
    return jsonify(res)
