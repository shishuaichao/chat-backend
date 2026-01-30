
friendships_can_update_field = ['status', 'remark']



def getFriendshipsByFriendId(cur, user_id, friend_id):
    if user_id == friend_id:
      return None
    try:
      cur.execute("SELECT * FROM friendships WHERE user_id=%s OR friend_id=%s", (friend_id, user_id))
      return cur.fetchone()
    except Exception as e:
      return None


def insertFriendship(cur, user_id, friend_id, status):
  try:
    cur.execute("INSERT INTO friendships (user_id, friend_id, status) VALUES (%s, %s, %s)", (user_id, friend_id, status))
    return cur.lastrowid
  except Exception as e:
    return None

def updateFriendships(cur, friendship_id, data):
    try:
      for item in data.items():
        if item[0] in friendships_can_update_field:
          sql = f"UPDATE friendships SET {item[0]}=%s WHERE id=%s"
          cur.execute(sql, (item[1], friendship_id))
      return True
    except Exception as e:
        return None