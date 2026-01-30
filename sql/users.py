from db_config import get_db

# 必传 username, nickname, password
def insertUserInfo(cur, username, nickname, password):
    cur.execute(
        "INSERT INTO users (username, nickname, password) VALUES (%s, %s, %s)",
        (username, nickname, password)
    )

# def getUserInfoById(cur, id):
#     cur.execute("SELECT id FROM users WHERE id=%s", (username,))