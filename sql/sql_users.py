
user_can_update_fields = ['nickname', 'avatar', 'password']

# 必传 username, nickname, password
def insertUserInfo(cur, username, nickname, password):
    cur.execute(
        "INSERT INTO users (username, nickname, password) VALUES (%s, %s, %s)",
        (username, nickname, password)
    )

def getUserInfoById(cur, user_id):
    if user_id is None:
        return None
    try:
        cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        return cur.fetchone()
    except Exception:
        return None

def updateUserInfoById(cur, id, data={}):
    if id is None:
        return None
    try:
        for item in data.items():
            if item[0] in user_can_update_fields:
                sql = f"UPDATE users SET {item[0]}=%s WHERE id=%s"
                cur.execute(sql, (item[1], id))
    except Exception:
        return None
