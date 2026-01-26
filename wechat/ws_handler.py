from flask_socketio import SocketIO, emit
from flask import request
from wechat.ws_utils import treat_socket_message, treat_socket_system_msg

# 核心存储：{sid: userInfo}，全局字典
user_map = {}

def register_socket_events(socketio): 
    # 客户端连接
    @socketio.on('connect')
    def handle_connect(auth):
        print(f"connect auth {auth}")
        sid = request.sid  # 获取客户端唯一标识（flask-socketio 内置）
        user_map[sid] = auth
        # print(f"✅连接成功 {sid} ，当前在线人数：{user_map}")
        # 给当前客户端发送连接成功提示
        emit('connect_success', sid)
        # 群发在线人数更新  
        emit('online_count', getUsersList(user_map), broadcast=True)
    _ = handle_connect

    # Socket.IO 事件：客户端断开连接
    @socketio.on('disconnect')
    def handle_disconnect():
        sid = request.sid
        if sid in user_map and user_map[sid] != '':
            print(f"❌断开连接（{user_map[sid]['userName']}）")
            # 移除用户
            del user_map[sid]
            # 群发在线人数更新  
            emit('online_count', getUsersList(user_map), broadcast=True)
    _ = handle_disconnect

    # 普通消息
    @socketio.on('message')
    def handle_socket_message(msgObj):
        treat_socket_message(msgObj)
    _ = handle_socket_message

    # 系统消息
    @socketio.on('system_msg')
    def handle_socket_system_msg(msgObj):
        treat_socket_system_msg(msgObj)
    _ = handle_socket_system_msg

    # 查询在线人数
    @socketio.on('query_online_count')
    def handle_query_online(data):
        print(f"查询在线人数 {data}")
        emit('online_count', getUsersList(user_map), broadcast=True)
    _ = handle_query_online

    def getUsersList(obj):

        return list(filter(lambda x: x != '', obj.values()))
    def getUsersList(data_dict):
        # 记录已出现的id，用于去重
        seen_ids = set()
        # 存储去重后的结果
        unique_values = []
        # 遍历字典的所有值（按插入顺序遍历，Python 3.7+ 字典保留插入顺序）
        for value in data_dict.values():
            # 获取当前项的id（如果没有id字段，跳过该条数据）
            item_id = value.get('userId')
            if item_id is None:
                continue
            # 仅保留首次出现的id对应的项
            if item_id not in seen_ids:
                seen_ids.add(item_id)
                unique_values.append(value)
        return unique_values