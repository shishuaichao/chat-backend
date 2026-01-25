# 导入其他文件的函数（核心：引用跨文件功能）
from db_operation import get_all_teachers, add_teacher
from flask import Flask, jsonify, render_template
from flask_cors import CORS  # 核心：解决跨域
from wechat.ws_handler import socketio  # 导入抽离的socketio实例
from wechat.operate import get_all_chats

app = Flask(__name__)
# 核心作用：为Flask应用设置加密密钥，用于cookie/会话/WS鉴权等加密
app.config['SECRET_KEY'] = 'secret'
CORS(app)  # 允许前端跨域请求

# 绑定socketio到app
socketio.init_app(app, cors_allowed_origins="*")

@app.route('/api/wechats', methods=['GET'])
def get_chats():
    res = get_all_chats()
    return jsonify(res)

@app.route('/', methods=['GET'])
def get_index():
    return render_template('index.html')



if __name__ == '__main__':
    socketio.run(app, host='172.20.10.2', port=5000, debug=True)

