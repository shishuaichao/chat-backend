
from .sql_conv_member import insertConvMember

conv_can_update_fields = ['name', 'avatar', 'password']

# 创建会话 必传 type_, name, owner_id, member_ids
def createConv(cur, type_, name, owner_id, member_ids):
    # 插入会话
    cur.execute(
        "INSERT INTO conversations (type, name, owner_id) VALUES (%s, %s, %s)",
        (type_, name, owner_id)
    )
    conv_id = cur.lastrowid
    # 插入成员
    for item in member_ids:
        insertConvMember(cur, conv_id, item['id'])
    return conv_id


# 