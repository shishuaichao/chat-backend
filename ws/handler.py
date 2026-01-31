from flask_socketio import emit, join_room, leave_room
from flask import request
from .utils import treat_socket_system_msg
from extensions import socketio
from sql.sql_messages import insert_message, get_message
from db_config import get_db
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
    emit('join_room', f"用户 {obj['userId']} 加入会话 {obj['roomId']}")
    print(f"✅用户 {obj['userId']} 加入会话 {obj['roomId']}")

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
        print('msg_info', msg_info)
        db.commit()
    emit('message', {
        'msgId': msg_id,
        'sender_id': msg_info['sender_id'],
        'convId': msg_info['conversation_id'],
        'type': msg_info['type'],
        'content': msg_info['content'],
        'avatar': msgObj['avatar'],
        'created_at': msg_info['created_at'].strftime("%H:%M:%S"),
    }, room=msgObj['convId'])

# 系统消息
@socketio.on('system_msg')
def handle_socket_system_msg(msgObj):
    treat_socket_system_msg(msgObj)

