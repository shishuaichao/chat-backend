from db_config import get_db

user_can_update_fields = ['nickname', 'avatar', 'password']

# 必传 username, nickname, password
def insertUserInfo(cur, username, nickname, password):
    cur.execute(
        "INSERT INTO users (username, nickname, password) VALUES (%s, %s, %s)",
        (username, nickname, password)
    )

def getUserInfoById(cur, id):
    cur.execute("SELECT * FROM users WHERE id=%s", (id,))
    return cur.fetchone()

def updateUserInfoById(cur, id, data={}):
    for item in data.items():
        if item[0] in user_can_update_fields:
            print('updateUserInfoById', item[0], item[1])
            sql = f"UPDATE users SET {item[0]}=%s WHERE id=%s"
            cur.execute(sql, (item[1], id))
