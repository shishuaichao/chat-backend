
friendships_can_update_field = ['status', 'remark']



def getFriendshipsByFriendId(cur, user_id, friend_id):
    if user_id == friend_id:
      return None
    try:
      cur.execute("SELECT * FROM friendships WHERE user_id=%s OR friend_id=%s", (user_id, friend_id))
      return cur.fetchone()
    except:
      return None



def insertFriendship(cur, user_id, friend_id, status):
  try:
    cur.execute("INSERT INTO friendships (user_id, friend_id, status) VALUES (%s, %s, %s)", (user_id, friend_id, status))
    return cur.lastrowid
  except:
    return None
  
# 更新好友关系内容
def updateFriendshipsById(cur, friendship_id, data):
    try:
      for item in data.items():
        if item[0] in friendships_can_update_field:
          sql = f"UPDATE friendships SET {item[0]}=%s WHERE id=%s"
          cur.execute(sql, (item[1], friendship_id))
      return True
    except:
        return None
    
def updateFriendshipsByFriendId(cur, user_id, friend_id, data):
    print('updateFriendshipsByFriendId', user_id, friend_id, data)
    try:
      for item in data.items():
        if item[0] in friendships_can_update_field:
          sql = f"UPDATE friendships SET {item[0]}=%s WHERE user_id=%s AND friend_id=%s"
          cur.execute(sql, (item[1], user_id, friend_id))
      return True
    except:
        return None