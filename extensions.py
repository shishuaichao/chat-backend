
from flask_socketio import SocketIO

socketio = SocketIO()  # 暂不绑定app，仅作为事件注册的载体

# def create_socketio(app):
#     socketio = SocketIO(
#         app,
#         async_mode='eventlet',  # 核心：指定 eventlet 模式，不依赖 Werkzeug
#         cors_allowed_origins="*"  # 允许跨域，生产环境指定具体域名
#     )
#     return socketio

