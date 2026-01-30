
from flask import Blueprint, jsonify, request
from db_config import get_db
from utils.response import resJson

from .chat_config import api_chat, chat_bp
from sql.sql_conv import createConv
from sql.sql_friendships import updateFriendshipsByFriendId, getFriendshipsInfo_userInfo
from sql.sql_conv import getConvIdBySessionKey, getConvMembers
from sql.sql_users import getUserInfoById


# 1. 创建会话（私聊/群聊）
@chat_bp.route(api_chat.create_conv, methods=['POST'])
def create_conv():
    data = request.json
    type_ = data['type']  # 1=私聊 2=群聊
    user_id = data['userId'] 
    member_ids = data['memberIds']  # 成员ID列表
    friend_id = data.get('friendId', '')
    conv_name = data.get('convName', '')  # 会话名称
    db = get_db()
    with db.cursor() as cur:
        conv_id = createConv(cur, type_, conv_name, user_id, member_ids)
        if type_ == '1':
            updateFriendshipsByFriendId(cur, user_id, friend_id, {'conversation_id': conv_id})
            updateFriendshipsByFriendId(cur, friend_id, user_id, {'conversation_id': conv_id})
        db.commit()
    return resJson(200, "创建成功", {"convId": conv_id})

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
                "SELECT type, name, avatar FROM conversations WHERE id=%s",
                (convId,)
            )
            convDetail = cur.fetchone()
            print('convDetail', convDetail)
            if convDetail['type'] == 1:
                cur.execute(
                    "SELECT friend_id, remark FROM friendships WHERE conversation_id=%s AND user_id=%s",
                    (convId, user_id)
                )
                friendshipInfo = cur.fetchone()
                friend_id = friendshipInfo['friend_id']
                cur.execute(
                    "SELECT nickname, avatar FROM users WHERE id=%s",
                    (friend_id,)
                )
                friendInfo = cur.fetchone()
                convDetail.update(friendshipInfo)
                convDetail.update(friendInfo)
            res_list.append({
                **convDetail, 'convId': convId})
    return jsonify({
        "code": 200, 
        "msg": "会话列表获取成功", 
        "data": res_list
    })

# 获取canvId 必传 session_key
@chat_bp.route('/conversation/getIdBySessionKey', methods=['GET'])
def get_conv_id_by_session_key():
    session_key = request.args.get('sessionKey')
    db = get_db()
    with db.cursor() as cur:
        conv_id = getConvIdBySessionKey(cur, session_key)
    return resJson(200, "会话ID获取成功", {"convId": conv_id})



# 获取会话详情
@chat_bp.route('/conversation/info', methods=['GET'])
def get_conv_info():
    conv_id = request.args.get('convId')   
    user_id = request.args.get('userId') 
    conv_type = request.args.get('type')
    db = get_db()
    with db.cursor() as cur:
        if conv_type == '1':
            convMembers = getConvMembers(cur, conv_id)
            for item in convMembers:
                if item['user_id'] != int(user_id):
                    friendId = item['user_id']
                    break
            froendships_info = getFriendshipsInfo_userInfo(cur, user_id, friendId)
            print('froendships_info', froendships_info)
            friend_info = getUserInfoById(cur, friendId)
            return resJson(200, "会话详情获取成功", {
                **friend_info, 
                'remark': froendships_info['remark']
            })
        else:
            cur.execute(
                "SELECT name, avatar FROM conversations WHERE id=%s",
                (conv_id,)
            )
            info = cur.fetchone()
    return jsonify({
        "code": 200, 
        "msg": "会话详情获取成功", 
        "data": {
            **info,
            'friendId': friendId,
            
        }
    })







