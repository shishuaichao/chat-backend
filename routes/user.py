

from flask import request
import hashlib
from .user_config import user_bp, api_user
from db_config import get_db
from utils.response import resJson
from sql.sql_users import (
     insertUserInfo, 
     updateUserInfoById, 
     getUserInfoById,
)
from sql.sql_friendships import (
  getFriendshipsInfoByFriendId, 
  insertFriendship, 
  updateFriendshipsById, 
  updateFriendshipsByFriendId, 
  getFriendListByUserId,
  getFriendApplyListByUserId,
)

# 1. 注册用户
@user_bp.route(api_user.register, methods=['POST'])
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

# 2. 查询当前用户信息
@user_bp.route(api_user.info, methods=['GET'])
def get_user_info():
    user_id = request.args.get("userId")
    db = get_db()
    with db.cursor() as cur:
        user = getUserInfoById(cur, user_id)
    return resJson(200, '用户信息查询成功', user)

# 3. 更新用户信息
@user_bp.route(api_user.update, methods=['POST'])
def update_user():
    data = request.json
    user_id = data['userId']
    db = get_db()
    with db.cursor() as cur:
        updateUserInfoById(cur, user_id, data)
        db.commit()
        user = getUserInfoById(cur, user_id)
    return resJson(200, '用户信息更新成功', user)

# 4. 申请/同意/添加好友
@user_bp.route(api_user.friend_add, methods=['POST'])
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
@user_bp.route(api_user.set_remark, methods=['POST'])
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
    return resJson(200, "好友备注成功")

# 6. 获取好友列表
@user_bp.route(api_user.friend_list, methods=['GET'])
def get_friendship_list():
    user_id = request.args.get('userId')
    db = get_db()
    with db.cursor() as cur:
        # 查询好友关系
        user_list = getFriendListByUserId(cur, user_id)
    return resJson(200, "好友列表获取成功", user_list)

# 7. 获取单条好友信息
@user_bp.route(api_user.friend_info, methods=['GET'])
def get_friendship_info():
    user_id = request.args.get("userId")
    friend_id = request.args.get("id")
    db = get_db()
    with db.cursor() as cur:
        user = getUserInfoById(cur, friend_id)
        if not user:
            return resJson(400, '用户不存在')
        else:
            if user_id != friend_id:
                friendship = getFriendshipsInfoByFriendId(cur, user_id, friend_id)
                if friendship:
                    user['friendshipsStatus'] = friendship['status']
                    user['remark'] = friendship['remark']
    return resJson(200, '好友信息查询成功', user)

# 8. 好友申请列表
@user_bp.route(api_user.friend_apply_list, methods=['GET'])
def get_friends_apply():
    user_id = request.args.get('userId')
    print(f"user_id{user_id}")
    db = get_db()
    with db.cursor() as cur:
        friendlist = getFriendApplyListByUserId(cur, user_id)
    return resJson(200, "好友申请列表获取成功", friendlist)



# 9. 获取群列表
@user_bp.route(api_user.group_list, methods=['GET'])
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
    return resJson(200, "群列表获取成功", group_list)





