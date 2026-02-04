
from .sql_conv_member import insertConvMember
from utils.getSessionKey import getSessionKey



conv_can_update_fields = ['name', 'avatar', 'password']

# 创建会话 必传 type_, name, owner_id, member_ids
def createConv(cur, type_, name, owner_id, member_ids):
    # 插入会话
    if int(type_) == 1:
        cur.execute(
            "INSERT INTO conversations (type, name, owner_id, session_key) VALUES (%s, %s, %s, %s)",
            (type_, name, owner_id, getSessionKey(member_ids))
        )
    else:
        cur.execute(
            "INSERT INTO conversations (type, name, owner_id) VALUES (%s, %s, %s)",
            (type_, name, owner_id)
        )
    conv_id = cur.lastrowid
    # 插入成员
    for item in member_ids:
        insertConvMember(cur, conv_id, item['id'])
    return conv_id


# get conversation by session key
def getConvIdBySessionKey(cur, session_key):
    cur.execute(
        "SELECT id FROM conversations WHERE session_key = %s",
        (session_key,)
    )
    conv_Info = cur.fetchone()
    return conv_Info['id'] if conv_Info else None

def getConvInfo(cur, conv_id):
    cur.execute(
        "SELECT * FROM conversations WHERE id = %s",
        (conv_id,)
    )
    conv_Info = cur.fetchone()
    return conv_Info if conv_Info else None

# 获取所有群
def getAllGroups(cur):
    cur.execute(
        "SELECT * FROM conversations WHERE type = 2"
    )
    conv_Info = cur.fetchall()
    return conv_Info if conv_Info else None

# 获取群信息
def getGroupInfo(cur, group_id):
    cur.execute(
        "SELECT * FROM conversations WHERE id = %s",
        (group_id,)
    )
    conv_Info = cur.fetchone()
    return conv_Info if conv_Info else None