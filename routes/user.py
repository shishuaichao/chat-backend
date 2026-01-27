
from flask import Blueprint, jsonify, request
import hashlib
from db_config import get_db
from utils.sql.get_valid_data import get_valid_data


# 1. 创建蓝图（参数：蓝图名、模块名、URL前缀）
user_bp = Blueprint(
    "user",          # 蓝图唯一标识
    __name__,          # 当前模块名
    url_prefix="/user"  # 该蓝图下所有路由的统一前缀（可选，简化路由）
)

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = hashlib.md5(data['password'].encode()).hexdigest()
    nickname = data.get('nickname', username)
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        if cur.fetchone():
            return jsonify({"code": 400, "msg": "用户名已存在"}), 400
        cur.execute(
            "INSERT INTO users (username, nickname, password) VALUES (%s, %s, %s)",
            (username, nickname, password)
        )
        db.commit()
    return jsonify({
        "code": 200, 
        "msg": "注册成功", 
        "data": {"username": username, "nickname": nickname}
    }) 

@user_bp.route('/update', methods=['POST'])
def update_user():
    data = request.json
    username = data['username']
    db = get_db()
    with db.cursor() as cur:
        # 查询用户ID
        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        if not user:
            return jsonify({"code": 400, "msg": "用户不存在"}), 400
        id = user['id']
        valid_fields = {"nickname", "type", "avatar", "password"}
        valueData = get_valid_data(data, valid_fields)
        cur.execute(f"UPDATE users SET {valueData['keys']} WHERE id=%s", (valueData['values'], id))
        db.commit()

    return jsonify({
        "code": 200, 
        "msg": "用户信息更新成功", 
        "data": {"username": username}
    })

@user_bp.route('/login', methods=['POST'])  
def login():
    return jsonify({'message': 'Login success'}), 200 
