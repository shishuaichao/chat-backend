
from flask import Blueprint, jsonify, request
import hashlib
from db_config import get_db
from sql.users import insertUserInfo
from utils.response import resJson


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
        insertUserInfo(cur, username, nickname, password)
        id = cur.lastrowid
        print('id', id)
        db.commit()
    data = {"username": username, "nickname": nickname, "id": id}
    return resJson(200, '注册成功', data)
    # return jsonify({
    #     "code": 200, 
    #     "msg": "注册成功", 
    #     "data": {"username": username, "nickname": nickname, "id": id}
    # }) 

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
@user_bp.route('/userInfo', methods=['GET'])
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
        try:
            # 查询好友关系
            cur.execute(
                'SELECT status, remark, conversation_id FROM friendships WHERE user_id=%s AND friend_id=%s', 
                (user_id, id)
            )
            friendships = cur.fetchone()
        except Exception as e:
            print(f"查询失败：{e}")
            return jsonify({
                "code": 200,
                "msg": "用户",
                "data": {
                    "id": user['id'], 
                    "username": user['username'],
                    "nickname": user['nickname'],
                    "avatar": user['avatar'],
                }
            })
    return jsonify({
        "code": 200, 
        "msg": "用户信息获取成功", 
        "data": {
            "id": user['id'], 
            "username": user['username'],
            "nickname": user['nickname'],
            "avatar": user['avatar'],
            "friendshipsStatus":  friendships['status'] if friendships else None,
            "remark": friendships['remark'] if friendships else None,
            "convId": friendships['conversation_id'] if friendships else None
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

# 好友备注
@user_bp.route('/friendship/remark', methods=['POST'])
def remark_friendship():
    data = request.json
    user_id = data['userId']
    friend_id = data['friendId']
    remark = data['remark']
    db = get_db()
    with db.cursor() as cur:
        # 更新好友备注
        cur.execute("UPDATE friendships SET remark=%s WHERE user_id=%s AND friend_id=%s", (remark, user_id, friend_id))
        db.commit()
    return jsonify({
        "code": 200, 
        "msg": "好友备注成功", 
        "data": {"remark": remark}
    })

# 获取好友列表
@user_bp.route('/friends', methods=['GET'])
def get_friendship_list():
    user_id = request.args.get('userId')
    db = get_db()
    with db.cursor() as cur:
        # 查询好友关系
        cur.execute("SELECT * FROM friendships WHERE user_id=%s AND status=1", (user_id,))
        friendships = cur.fetchall()
        user_list = []
        for item in friendships:
            cur.execute("SELECT id, username, nickname, avatar FROM users WHERE id=%s", (item['friend_id'],))
            friend_info = cur.fetchone()
            if friend_info:
                user_info = {
                    "id": item['friend_id'],
                    "remark": item['remark'],
                    "conversationId": item['conversation_id'],
                    "username": friend_info['username'],
                    "nickname": friend_info['nickname'],
                    "avatar": friend_info['avatar'],
                }
                user_list.append(user_info)
    return jsonify({
        "code": 200, 
        "msg": "好友列表获取成功", 
        "data": user_list
    })

# 获取群列表
@user_bp.route('/groups', methods=['GET'])
def get_group_list():
    user_id = request.args.get('userId')
    print('user_id', user_id)
    db = get_db()
    with db.cursor() as cur:
        # 查询群关系
        cur.execute("SELECT conversation_id FROM conversation_members WHERE user_id=%s", (user_id,))
        convList = cur.fetchall()
        print('convList', convList)
        group_list = []
        for item in convList:
            convId = item['conversation_id']
            cur.execute("SELECT id, name, avatar FROM conversations WHERE id=%s", (convId,))
            group_info = cur.fetchone()
            if group_info:
                group_list.append(group_info)
        
    return jsonify({
        "code": 200, 
        "msg": "群列表获取成功", 
        "data": group_list
    })

# 好友申请列表
@user_bp.route('/friends/apply', methods=['GET'])
def get_friends_apply():
    user_id = request.args.get('userId')
    print(f"user_id{user_id}")
    db = get_db()
    with db.cursor() as cur:
        cur.execute("SELECT * FROM friendships WHERE friend_id=%s", (user_id,))
        itemList = cur.fetchall()
        userList = []
        for item in itemList:
            cur.execute("SELECT * FROM users WHERE id=%s", (item["user_id"]))
            userItem = cur.fetchone()
            if item['status'] == 3 and userItem:
                userList.append({**userItem, "status": 3})
    return jsonify({
        "code": 200, 
        "msg": "列表获取成功", 
        "data": userList
    })



