
from flask import Flask
from flask_cors import CORS  # 核心：解决跨域
from routes import all_blueprints
from extensions import socketio
import ws.handler

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    app.config['WTF_CSRF_ENABLED'] = True  # 开启CSRF保护
    # 注册蓝图（延迟导入，避免循环依赖）
    for bp in all_blueprints:
        app.register_blueprint(bp)
    CORS(app)  # 允许前端跨域请求
    socketio.init_app(
        app,
        async_mode='eventlet',  # 指定eventlet模式
        cors_allowed_origins="*"  # 跨域配置
    )
    return app

app = create_app()

if __name__ == '__main__':
    socketio.run(app, host='192.168.1.5', port=5000, debug=True)
    # socketio.run(app, host='172.20.10.2', port=5000, debug=True)


