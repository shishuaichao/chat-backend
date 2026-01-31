
from flask_socketio import SocketIO

# socketio = SocketIO()  # 暂不绑定app，仅作为事件注册的载体
# 配置心跳
socketio = SocketIO(heartbeat_timeout=10, heartbeat_interval=1)



