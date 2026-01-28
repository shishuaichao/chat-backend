
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
        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        userId = cur.fetchone()['id']
    return jsonify({
        "code": 200, 
        "msg": "注册成功", 
        "data": {"username": username, "nickname": nickname, "id": userId}
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
        # valid_fields = {"nickname", "type", "avatar", "password"}
        # valueData = get_valid_data(data, valid_fields)
        # cur.execute(f"UPDATE users SET {valueData['keys']} WHERE id=%s", (valueData['values'], id))
        if 'nickname' in data:
            cur.execute("UPDATE users SET nickname=%s WHERE id=%s", (data['nickname'], id))
        if 'avatar' in data:
            cur.execute("UPDATE users SET avatar=%s WHERE id=%s", (data['avatar'], id))
        db.commit()
    return jsonify({
        "code": 200, 
        "msg": "用户信息更新成功", 
        # "data": {
        #     "id": user['id'], 
        #     "username": user['username'],
        #     "nickname": data.get('nickname', user.get('nickname', '')), 
        #     "avatar": data.get('avatar', user.get('avatar', ''))
        # }
    })

# 3. 获取用户信息+好友关系
@user_bp.route('/info', methods=['GET'])
def get_user_info():
    user_id = request.args.get("userId")
    id = request.args.get("id")
    db = get_db()
    with db.cursor() as cur:
        # 查询用户信息
        cur.execute('SELECT id, username, nickname, avatar FROM users WHERE id=%s', (id,))
        user = cur.fetchone()
        if not user:
            return jsonify({"code": 400, "msg": "用户不存在"}), 400
        # 查询好友关系
        cur.execute('SELECT status FROM friendships WHERE user_id=%s AND friend_id=%s', (user_id, id))
        friendships = cur.fetchone()
    return jsonify({
        "code": 200, 
        "msg": "用户信息获取成功", 
        "data": {
            "id": user['id'], 
            "username": user['username'],
            "nickname": user['nickname'],
            "avatar": user['avatar'],
            "friendshipsStatus": friendships['status'] if friendships else None
        }
    })

# 4. 获取所有用户
@user_bp.route('/all', methods=['GET'])
def get_all_users():
    db = get_db()
    with db.cursor() as cur:
        cur.execute('SELECT id, username, nickname, avatar FROM users')
        users = cur.fetchall()
    return jsonify({
        "code": 200, 
        "msg": "所有用户信息获取成功", 
        "data": users
    })

# 添加好友
@user_bp.route('/friendship/add', methods=['POST'])
def add_friendship():
    data = request.json
    user_id = data['userId']
    friend_id = data['friendId']
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id FROM friendships WHERE user_id=%s AND friend_id=%s", (user_id, friend_id))
        friendship = cur.fetchone()
        if friendship:
            return jsonify({"code": 200, "msg": "已申请，待确认"}), 200
        cur.execute("select id from friendships where user_id=%s AND friend_id=%s", (friend_id, user_id))
        friendship = cur.fetchone()
        if friendship:
            cur.execute('update friendships set status=1 where user_id=%s AND friend_id=%s', (friend_id, user_id))
            cur.execute("INSERT INTO friendships (user_id, friend_id, status) VALUES (%s, %s, %s)", (user_id, friend_id, 1))
            db.commit()
            return jsonify({
                "code": 200, 
                "msg": "添加好友成功", 
                "data": {"friendshipsStatus": 1},
            })    
            # 添加会话
            # cur.execute(
            #     "INSERT INTO conversations (type, name, owner_id) VALUES (%s, %s, %s)",
            #     (1, f"{user_id}_{friend_id}", user_id)
            # )
            # conv_id = cur.lastrowid
            # # 会话插入成员
            # for itemId in [user_id, friend_id]:
            #     cur.execute(
            #         "INSERT INTO conversation_members (conversation_id, user_id) VALUES (%s, %s)",
            #         (conv_id, itemId)
            #     )
            # # 会话加到friendship中
            # cur.execute(
            #     "INSERT INTO friendships (user_id, friend_id, status, conversation_id) VALUES (%s, %s, %s, %s)",
            #     (user_id, friend_id, 1, conv_id)
            # )
        
        cur.execute("INSERT INTO friendships (user_id, friend_id, status) VALUES (%s, %s, %s)", (user_id, friend_id, 3))
        db.commit()
    return jsonify({
        "code": 200, 
        "msg": "好友申请成功，待确认", 
        "data": {"friendshipsStatus": 3},
    })

# 确认好友
@user_bp.route('/friendship/confirm', methods=['POST'])
def confirm_friendship():
    data = request.json
    user_id = data['userId']
    friend_id = data['friendId']
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT id FROM friendships WHERE user_id=%s AND friend_id=%s AND status=3", (user_id, friend_id))
        friendship = cur.fetchone()
        if not friendship:
            return jsonify({"code": 400, "msg": "好友申请不存在"}), 400
        # 更新好友关系为已确认
        cur.execute("UPDATE friendships SET status=1 WHERE id=%s", (friendship['id'],))
        db.commit()
    return jsonify({
        "code": 200, 
        "msg": "好友确认成功", 
        "data": {"friendshipsStatus": 1}
    })






