
from flask import Blueprint, jsonify, request
from db_config import get_db
from utils.response import resJson

from .chat_config import api_chat, chat_bp
from sql.sql_conv import createConv
from sql.sql_friendships import updateFriendshipsByFriendId, getFriendshipsInfo_userInfo
from sql.sql_conv import getConvIdBySessionKey, getAllGroups
from sql.sql_users import getUserInfoById
from sql.sql_messages import get_messages_records, getConvMemberUnreadInfoList, getLastMessage
from sql.sql_conv_member import updateConvMemberUnreadInfo, getConvMemberUnreadInfo, getConvMembersInfo


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
    conv_id = data['convId']
    user_id = data['userId']
    print('conv_id', conv_id)
    db = get_db()
    with db.cursor() as cur:
        # 检查用户是否已加入会话
        cur.execute(
            "SELECT id FROM conversation_members WHERE conversation_id=%s AND user_id=%s",
            (conv_id, user_id)
        )
        if cur.fetchone():
            return resJson(200, "用户加入会话成功")
        # 加入会话
        cur.execute(
            "INSERT INTO conversation_members (conversation_id, user_id) VALUES (%s, %s)",
            (conv_id, user_id)
        )
        db.commit()
        return resJson(200, "用户加入会话成功")

# 获取对应会话中的所有聊天记录
@chat_bp.route('/records', methods=['GET'])
def get_messages_xxxrecords():
    conv_id = request.args.get('convId')
    user_id = request.args.get('userId')
    # print('conv_id', conv_id)
    db = get_db()
    with db.cursor() as cur:
        records = get_messages_records(cur, conv_id)
        
        arr = []
        for record in records:
            user_info = getUserInfoById(cur, record['sender_id'])
            unreadInfo = getConvMemberUnreadInfo(cur, conv_id, user_id)
            # 设置未读数量
            obj = {
                'id': record['id'],
                'content': record['content'],
                'senderId': user_info['id'],
                'senderNickname': user_info['nickname'],
                'name': user_info['nickname'],
                'avatar': user_info['avatar'],
                'msgType': record['type'],
                'createTime': record['created_at'].strftime("%H:%M:%S"),
            }
            arr.append(obj)
    return resJson(200, "聊天记录获取成功", {
        "records": arr,
        "last_read_msg_id": unreadInfo['last_read_msg_id'],
        "unread_count": unreadInfo['unread_count'],
    })



# 获取会话中所有成员的未读信息列表
@chat_bp.route(api_chat.get_conv_member_unread_list, methods=['GET'])
def get_conv_member_unread_list():
    conv_id = request.args.get('convId')
    last_read_msg_id = request.args.get('lastReadMsgId')
    if not last_read_msg_id:
        last_read_msg_id = 0
    db = get_db()
    with db.cursor() as cur:
        unreadInfoList = getConvMemberUnreadInfoList(cur, conv_id, last_read_msg_id)
        for record in unreadInfoList:
            print('record', record)
            sender_info = getUserInfoById(cur, record['sender_id'])
            print('sender_info', sender_info)
            record['senderNickname'] = sender_info['nickname']
            record['avatar'] = sender_info['avatar']
            record['createTime'] = record['created_at'].strftime("%H:%M:%S")
        return resJson(200, "未读信息列表获取成功", unreadInfoList)

# 更新会话中成员的未读状态
@chat_bp.route(api_chat.update_conv_member_unread, methods=['POST'])
def update_conv_member_unread_info():
    data = request.json
    user_id = data['userId']
    conv_id = data['convId']
    last_read_msg_id = data['lastReadMsgId'],
    db = get_db()
    with db.cursor() as cur:
        # 更新会话中成员的未读状态
        updateConvMemberUnreadInfo(cur, conv_id, user_id, last_read_msg_id)
        db.commit()
    return resJson(200, "未读状态更新成功")

# 获取会话列表
@chat_bp.route('/conversation/list', methods=['GET'])
def get_conv_list():
    user_id = request.args.get('userId')
    db = get_db()
    with db.cursor() as cur:
        user_info = getUserInfoById(cur, user_id)
        groupList = getAllGroups(cur)
        arr = []
        obj = {}
        for item in groupList:
            msg_info = getLastMessage(cur, item['id'])
            member_info = getConvMemberUnreadInfo(cur, item['id'], user_id)
            obj = {
                'convId': item['id'],
                'convType': item['type'],
                'name': item['name'],
                'avatar': item['avatar'],
                'id': msg_info['id'],
                'content': msg_info['content'],
                'msgType': msg_info['type'],
                'createTime': msg_info['created_at'].strftime("%H:%M"),
                'senderId': msg_info['sender_id'],
                'senderNickname': user_info['nickname'],

                'unreadCount': member_info['unread_count'],
            }
            arr.append(obj)
    return resJson(200, "会话列表获取成功", arr)
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
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT name FROM conversations WHERE id=%s",
            (conv_id,)
        )
        info = cur.fetchone()
    return jsonify({
        "code": 200, 
        "msg": "会话详情获取成功", 
        "data": info
    })

# 获取会话成员
@chat_bp.route('/conversation/member', methods=['GET'])
def get_conv_members():
    conv_id = request.args.get('convId')
    db = get_db()
    member_list = []
    with db.cursor() as cur:
        convMemberIds = getConvMembersInfo(cur, conv_id)
        for item in convMemberIds:
            userInfo = getUserInfoById(cur, item['user_id'])
            member_list.append(userInfo)
    return resJson(200, "会话成员获取成功", member_list)





