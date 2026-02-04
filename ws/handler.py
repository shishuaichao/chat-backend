from flask_socketio import emit, join_room, leave_room
from flask import request
from .utils import treat_socket_system_msg
from extensions import socketio
from sql.sql_messages import insert_message, get_message
from db_config import get_db
from sql.sql_conv_member import updateConvMemberUnreadInfo, getConvMembersInfo
import datetime
from sql.sql_users import getUserInfoById
from sql.sql_conv import getConvInfo

user_map = {}

# 客户端连接
@socketio.on('connect')
def handle_connect(auth):
    sid = request.sid
    authtoken = auth['authToken']
    user_map[authtoken] = sid
    print(f"✅连接成功 在线人数: {len(user_map)} 都有：{user_map}")
    emit('connect_success', {})

# 加入会话
@socketio.on('room:join')
def handle_room_join(obj):
    join_room(obj['roomId'])
    emit('join_room', { 'userId': obj['userId']}, broadcast=True)

# 离开会话
@socketio.on('room:leave')
def handle_room_leave(obj):
    leave_room(obj['roomId'])
    emit('leave_room', { 'userId': obj['userId']}, broadcast=True)

# Socket.IO 事件：客户端断开连接
@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in user_map.values():
        authtoken = next(key for key, value in user_map.items() if value == sid)
        print(f"❌断开连接 ID: {authtoken}")
        del user_map[authtoken]
        

# 消息
@socketio.on('message')
def handle_socket_message(msgObj):
    # userId // 发送者id
    # content // 消息内容
    # msgType // 消息类型 1: 文本 2: 图片 3: 语音 4: 视频 5: 文件 6: 位置 7: 链接 8: 系统消息
    # convId // 会话id
    # convType  // 会话类型 1: 单聊 2: 群聊
    # to  // 单聊接收者id
    print('msgObj', msgObj)
    db = get_db()
    with db.cursor() as cur:
        msg_id = insert_message(cur, msgObj)  # 插入消息
        msg_info = get_message(cur, msg_id)  # 获取消息
        from_info = getUserInfoById(cur, msgObj['userId']) # 发送人信息
        conv_info = getConvInfo(cur, msgObj['convId'])  # 获取会话信息
        
        
        # 再给房间外的人发消息
        if int(msgObj['convType']) == 1:
            # 单聊
            to_info = getUserInfoById(cur, msgObj['to']) # 接收人信息
            print('to_info', to_info)
            # 先给房间里发消息
            sendInfo = makeMessage(from_info, to_info, msg_info, conv_info) 
            # 更新对方的未读消息信息 and 给对方额外发一条消息，如果他不在房间内也能收到
            sendNoticeMsgToSomeoneForNotInRoom(sendInfo, user_map[msgObj['to']])
        elif (int(msgObj['convType']) == 2):
            # 群聊
            sendInfo = makeMessage(from_info, {}, msg_info, conv_info) 
            print('qun sendInfo', sendInfo)
            # 获取会话成员信息 and 更新成员的未读信息 and 发送消息
            convMembers = getConvMembersInfo(cur, msgObj['convId'])
            print('qun convMembers', convMembers)
            for member in convMembers:
                print('qun member', member)
                user_id = member['user_id']
                if (str(user_id) in user_map.keys()): 
                    print('qun user_map[user_id]', user_map[str(user_id)])
                    sendNoticeMsgToSomeoneForNotInRoom(sendInfo, user_map[str(user_id)])
        db.commit()
        emit('message', sendInfo, room=msgObj['convId'])
    
# 给不在房间的人发送消息
def sendNoticeMsgToSomeoneForNotInRoom(msgInfo, sid):
    emit('notice_message', msgInfo, to=sid)

# 系统消息
@socketio.on('system_msg')
def handle_socket_system_msg(msgObj):
    treat_socket_system_msg(msgObj)

# 返回消息格式
def makeMessage(from_info, to_info, msg_info, conv_info):
    if (conv_info['type'] == 1):
        name = to_info['nickname']
    else:
        name = conv_info['name']
    return {
        'id': msg_info['id'],
        'senderId': msg_info['sender_id'],
        'senderNickname': from_info['nickname'],
        'avatar': from_info['avatar'],

        'content': msg_info['content'],
        'msgType': msg_info['type'],
        'createTime': msg_info['created_at'].strftime("%H:%M:%S"),
        
        'name': name,

        'convId': conv_info['id'],
        'convType': conv_info['type'],

    }

