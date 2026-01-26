
from flask import Flask
from flask_cors import CORS  # 核心：解决跨域
from flask_socketio import SocketIO
from ws.handler import register_socket_events
from routes import all_blueprints

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    # 注册蓝图（延迟导入，避免循环依赖）
    for bp in all_blueprints:
        app.register_blueprint(bp)
    return app

app = create_app()

socketio = SocketIO(
    app,
    async_mode='eventlet',  # 核心：指定 eventlet 模式，不依赖 Werkzeug
    cors_allowed_origins="*"  # 允许跨域，生产环境指定具体域名
)
CORS(app)  # 允许前端跨域请求

# 绑定socketio到app
socketio.init_app(app, cors_allowed_origins="*")
register_socket_events(socketio)

if __name__ == '__main__':
    socketio.run(app, host='172.20.10.2', port=5000, debug=True)


