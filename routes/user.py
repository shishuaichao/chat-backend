
from flask import Blueprint, jsonify, request
import hashlib
from db_config import get_db
from utils.response import resJson
from sql.sql_users import insertUserInfo, updateUserInfoById, getUserInfoById
from sql.sql_friendships import (
  getFriendshipsInfoByFriendId, 
  insertFriendship, 
  updateFriendshipsById, 
  updateFriendshipsByFriendId, 
  getFriendListByUserId,
)


# 创建蓝图（参数：蓝图名、模块名、URL前缀）
user_bp = Blueprint(
    "user",          # 蓝图唯一标识
    __name__,          # 当前模块名
    url_prefix="/user"  # 该蓝图下所有路由的统一前缀（可选，简化路由）
)

# 1. 注册用户
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
    data = {"nickname": nickname, "id": id}
    return resJson(200, '注册成功', data)

# 2. 查询用户信息
@user_bp.route('/userInfo', methods=['GET'])
def get_user_info111():
    id = request.args.get("id")
    user_id = request.args.get("userId")
    db = get_db()
    with db.cursor() as cur:
        user = getUserInfoById(cur, id)
        if not user:
            return resJson(400, '用户不存在')
        else:
            if user_id != id:
                friendship = getFriendshipsInfoByFriendId(cur, user_id, id)
                if friendship:
                    user['friendshipsStatus'] = friendship['status']
                    user['remark'] = friendship['remark']
    return resJson(200, '用户信息查询成功', user)

# 3. 更新用户信息
@user_bp.route('/update', methods=['POST'])
def update_user():
    data = request.json
    user_id = data['userId']
    db = get_db()
    with db.cursor() as cur:
        updateUserInfoById(cur, user_id, data)
        db.commit()
        user = getUserInfoById(cur, user_id)
    return resJson(200, '用户信息更新成功', user)

# 4. 添加好友
@user_bp.route('/friendship/add', methods=['POST'])
def add_friendship():
	data = request.json
	user_id = data['userId']
	friend_id = data['friendId']
	db = get_db()
	with db.cursor() as cur:
		# 检查对方是否已申请好友
		friendship = getFriendshipsInfoByFriendId(cur, user_id, friend_id)
		if friendship:
			# 对方已申请好友
			insertFriendship(cur, user_id, friend_id, 1)
			updateFriendshipsById(cur, friendship['id'], {'status': 1})
			db.commit()
			return resJson(200, '添加成功', friendship)
		else:
			# 对方未申请好友
			insertFriendship(cur, user_id, friend_id, 3)
			db.commit()
			return resJson(200, '好友申请成功，待确认', friendship)

# 5. 好友设置备注
@user_bp.route('/friendship/remark', methods=['POST'])
def remark_friendship():
    data = request.json
    user_id = data['userId']
    friend_id = data['friendId']
    remark = data['remark']
    db = get_db()
    with db.cursor() as cur:
        # 更新好友备注
        updateFriendshipsByFriendId(cur, user_id, friend_id, {'remark': remark})
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
        user_list = getFriendListByUserId(cur, user_id)
    return jsonify({
        "code": 200, 
        "msg": "好友列表获取成功", 
        "data": user_list
    })






# 3. 获取用户信息+好友关系
@user_bp.route('/11userInfo111', methods=['GET'])
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



