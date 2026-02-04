

from .sql_users import getUserInfoById

friendships_can_update_field = ['status', 'remark']





# 插入好友关系
def insertFriendship(cur, user_id, friend_id, status):
  try:
    cur.execute("INSERT INTO friendships (user_id, friend_id, status) VALUES (%s, %s, %s)", (user_id, friend_id, status))
    return cur.lastrowid
  except:
    return None
  
# 更新好友关系内容（通过好友关系ID）
def updateFriendshipsById(cur, friendship_id, data):
    try:
      for item in data.items():
        if item[0] in friendships_can_update_field:
          sql = f"UPDATE friendships SET {item[0]}=%s WHERE id=%s"
          cur.execute(sql, (item[1], friendship_id))
      return True
    except:
        return None
# 更新好友关系内容（通过好友ID）
def updateFriendshipsByFriendId(cur, user_id, friend_id, data):
    try:
      for item in data.items():
        if item[0] in friendships_can_update_field:
          sql = f"UPDATE friendships SET {item[0]}=%s WHERE user_id=%s AND friend_id=%s"
          cur.execute(sql, (item[1], user_id, friend_id))
      return True
    except:
        return None

# 查询好友关系信息（通过好友ID）
def getFriendshipsInfo_friendInfo(cur, user_id, friend_id):
    if user_id == friend_id:
      return None
    try:
      cur.execute("SELECT * FROM friendships WHERE user_id=%s AND friend_id=%s", (friend_id, user_id))
      return cur.fetchone()
    except:
      return None
def getFriendshipsInfo_userInfo(cur, user_id, friend_id):
    if user_id == friend_id:
      return None
    try:
      cur.execute("SELECT * FROM friendships WHERE user_id=%s AND friend_id=%s", (user_id, friend_id))
      return cur.fetchone()
    except:
      return None
# 查询好友列表（通过用户ID）
def getFriendListByUserId(cur, user_id):
    friendlist = []
    try:
      cur.execute("SELECT * FROM friendships WHERE user_id=%s AND status=1", (user_id,))
      friendshipsList = cur.fetchall()
      for item in friendshipsList:
        friendInfo = getUserInfoById(cur, item['friend_id'])
        friendInfo['remark'] = item['remark']
        friendlist.append(friendInfo)
      return friendlist
    except:
      return None
# 查询好友申请列表（通过用户ID）
def getFriendApplyListByUserId(cur, user_id):
    try:
      cur.execute("SELECT * FROM friendships WHERE friend_id=%s AND status=3", (user_id,))
      friendlist = cur.fetchall()
      return friendlist
    except:
      return None

# 查询好友信息
def getFriendInfo(cur, user_id, friend_id):
    print('friendships', user_id, friend_id)
    cur.execute("SELECT * FROM friendships WHERE user_id=%s AND friend_id=%s", (user_id, friend_id))
    ship_info = cur.fetchone()
    friend_info = getUserInfoById(cur, friend_id)
    if ship_info:
      friend_info['remark'] = ship_info['remark']
    return friend_info

