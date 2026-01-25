from flask_socketio import SocketIO, emit
from wechat.operate import add_chat
import datetime
from flask import request
from wechat.ws_utils import treat_socket_message, treat_socket_system_msg

# 初始化socketio（空初始化，后续在app.py中绑定app）
socketio = SocketIO()

# 核心存储：{sid: userInfo}，全局字典
user_map = {}

# 客户端连接
@socketio.on('connect')
def handle_connect():
    sid = request.sid  # 获取客户端唯一标识（flask-socketio 内置）
    user_map[sid] = ''
    print(f"✅连接成功 {sid} ，当前在线人数：{user_map}")
    # 给当前客户端发送连接成功提示
    emit('connect_success', sid)
    # 群发在线人数更新  
    emit('online_count', getUsersList(user_map), broadcast=True)

# Socket.IO 事件：客户端断开连接
@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in user_map:
        # 通知所有客户端该用户已退出
        # emit('system_msg', { 
        #     'id': user_map[sid]['id'], 
        #     'content': f"{user_map[sid]['nickname']} 退出聊天", 
        #     'type': 'system_msg', 
        #     'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        # }, broadcast=True)
        print(f"❌断开连接（{user_map[sid]['nickname']}）")
        # 移除用户
        del user_map[sid]
        # 群发在线人数更新  
        emit('online_count', getUsersList(user_map), broadcast=True)

# 核心：监听前端传过来的用户名并存储
@socketio.on('set_nickname')
def handle_set_nickname(userInfo):
    sid = request.sid
    nickname = userInfo['nickname']
    # 判断是否重复昵称
    # if not any(userInfo['id'] == item['id'] for item in user_map.values() if item is not None):
    user_map[sid] = userInfo
    emit('online_count', getUsersList(user_map), broadcast=True)
    print(f"✅连接成功 是设置昵称 {sid} ，当前在线人数：{user_map}")
    # msgData = {
    #     'id': userInfo['id'],
    #     'content': f'{nickname} 已加入聊天室',
    #     'type': 'system_msg',
    #     'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    # }
    # emit('system_msg', msgData, broadcast=True)  # 广播给所有客户端
    # print(msgData)
    # add_chat(msgData)

# 普通消息
@socketio.on('message')
def handle_socket_message(msgObj):
    treat_socket_message(msgObj)

# 系统消息
@socketio.on('system_msg')
def handle_socket_system_msg(msgObj):
    treat_socket_system_msg(msgObj)

def getUsersList(obj):
    return list(filter(lambda x: x != '', obj.values()))