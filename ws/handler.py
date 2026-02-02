from flask_socketio import emit, join_room, leave_room
from flask import request
from .utils import treat_socket_system_msg
from extensions import socketio
from sql.sql_messages import insert_message, get_message
from db_config import get_db
from sql.sql_conv_member import updateConvMemberUnreadInfo
import datetime

user_map = {}

# 客户端连接
@socketio.on('connect')
def handle_connect(auth):
    sid = request.sid
    authtoken = auth['authToken']
    user_map[sid] = authtoken
    print(f"✅连接成功 ID: {authtoken} ，在线人数: {len(user_map)} 都有：{user_map}")
    emit('connect_success')

# 加入会话
@socketio.on('room:join')
def handle_room_join(obj):
    join_room(obj['roomId'])
    noticeMsg = f"用户加入 {obj['userId']} 加入会话 {obj['roomId']}"
    emit('join_room', noticeMsg, broadcast=True)
    print(noticeMsg)

# 离开会话
@socketio.on('room:leave')
def handle_room_leave(obj):
    leave_room(obj['roomId'])
    emit('leave_room', f"用户ID: {obj['userId']} 离开会话", broadcast=True)
    print(f"✅用户离开 {obj['userId']} 离开会话 {obj['roomId']}")

# Socket.IO 事件：客户端断开连接
@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in user_map:
        print(f"❌断开连接 ID: {user_map[sid]}")
        del user_map[sid]
        

# 普通消息
@socketio.on('message')
def handle_socket_message(msgObj):
    db = get_db()
    with db.cursor() as cur:
        msg_id = insert_message(cur, msgObj)
        msg_info = get_message(cur, msg_id)
        # print('msg_info', msg_info)
        db.commit()
    emit('message', makeMessage(msg_id, msg_info, msgObj), room=msgObj['convId'])

# 私聊消息
@socketio.on('private_message')
def handle_private_message(msgObj):
    print(f"收到私聊: {msgObj}")
    # 检查接收者是否在线
    sid = request.sid
    # 入库
    db = get_db()
    with db.cursor() as cur:
        msg_id = insert_message(cur, msgObj)
        msg_info = get_message(cur, msg_id)
        updateConvMemberUnreadInfo(cur, msgObj['convId'], msgObj['from'], msg_id)
        db.commit()
    for s_id in user_map.keys():
        if ( int(user_map[s_id]) == int(msgObj['to'])):
            emit('private_message', makeMessage(msg_id, msg_info, msgObj), to=s_id)
        elif (int(user_map[s_id]) == int(msgObj['from'])): 
            # 更新发送者的未读状态
            emit('message', makeMessage(msg_id, msg_info, msgObj), to=s_id)
            
    print(f"✅私聊: {msgObj['from']} 发送私聊消息给用户ID: {msgObj['to']}")


# 系统消息
@socketio.on('system_msg')
def handle_socket_system_msg(msgObj):
    treat_socket_system_msg(msgObj)

def makeMessage(msg_id, msg_info, msgObj):
    return {
        'id': msg_id,
        'sender_id': msg_info['sender_id'],
        'convId': msg_info['conversation_id'],
        'type': msg_info['type'],
        'content': msg_info['content'],
        'avatar': msgObj['avatar'],
        'created_at': msg_info['created_at'].strftime("%H:%M:%S"),
    }