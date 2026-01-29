
from flask import Blueprint, jsonify, request
from db_config import get_db
from ws.utils import convert_user_id_field

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
    user_id = data['userId']
    friend_id = data['friendId']
    member_ids = data['memberIds']  # 成员ID列表
    db = get_db()
    with db.cursor() as cur:
        # 插入会话
        cur.execute(
            "INSERT INTO conversations (type, name, owner_id) VALUES (%s, %s, %s)",
            (type_, '', user_id)
        )
        conv_id = cur.lastrowid
        # 插入成员
        for item in member_ids:
            cur.execute(
                "INSERT INTO conversation_members (conversation_id, user_id) VALUES (%s, %s)",
                (conv_id, item['id'])
            )
        if type_ == 1:
            # 更新用户关系
            cur.execute(
                "UPDATE friendships SET conversation_id=%s WHERE user_id=%s AND friend_id=%s",
                (conv_id, user_id, friend_id)
            )
            cur.execute(
                "UPDATE friendships SET conversation_id=%s WHERE user_id=%s AND friend_id=%s",
                (conv_id, friend_id, user_id)
            )
        db.commit()
    return jsonify({"code": 200, "data": {"convId": conv_id}, "msg": "创建成功"})

# 1. 加入会话
@chat_bp.route('/conversation/join', methods=['POST'])
def join_conv():
    data = request.json
    conv_id = data['conv_id']
    user_id = data['user_id']
    db = get_db()
    with db.cursor() as cur:
        # 检查会话是否存在
        cur.execute("SELECT id FROM conversations WHERE id=%s", (conv_id,))
        if not cur.fetchone():
            return jsonify({"code": 400, "msg": "会话不存在"}), 400
        # 检查用户是否已加入会话
        cur.execute(
            "SELECT id FROM conversation_members WHERE conversation_id=%s AND user_id=%s",
            (conv_id, user_id)
        )
        if cur.fetchone():
            return jsonify({"code": 400, "msg": "用户已加入会话"}), 400
        # 加入会话
        cur.execute(
            "INSERT INTO conversation_members (conversation_id, user_id) VALUES (%s, %s)",
            (conv_id, user_id)
        )
        db.commit()
    return jsonify({"code": 200, "msg": "用户加入会话成功"})

# 获取对应会话中的所有聊天记录
@chat_bp.route('/records', methods=['GET'])
def get_messages_records():
    conv_id = request.args.get('convId')
    print('conv_id', conv_id)
    db = get_db()
    with db.cursor() as cur:
        # 查询会话中的聊天记录
        cur.execute(
            "SELECT * FROM messages WHERE conversation_id=%s",
            (conv_id,)
        )
        records = cur.fetchall()
    return jsonify({
        "code": 200, 
        "msg": "聊天记录获取成功", 
        "data": records
    })


# 获取会话列表
@chat_bp.route('/conversation/list', methods=['GET'])
def get_conv_list():
    user_id = request.args.get('userId')
    db = get_db()
    with db.cursor() as cur:
        # 查询用户加入的会话
        cur.execute(
            "SELECT conversation_id FROM conversation_members WHERE user_id=%s",
            (user_id,)
        )
        convList = cur.fetchall()
        res_list = []
        for convItem in convList:
            convId = convItem['conversation_id']
            cur.execute(
                "SELECT name, type, avatar FROM conversations WHERE id=%s",
                (convId,)
            )
            convDetail = cur.fetchone()
            res_list.append({**convDetail, 'convId': convId})
    return jsonify({
        "code": 200, 
        "msg": "会话列表获取成功", 
        "data": res_list
    })









