

can_update_fields = ['role', 'unread_count', 'last_read_msg_id']

# 创建会话成员 必传 conversation_id, user_id
def insertConvMember(cur, conversation_id, user_id):
    cur.execute(
        "INSERT INTO conversation_members (conversation_id, user_id) VALUES (%s, %s)",
        (conversation_id, user_id)
    )

# 修改会话成员信息 (根据会话id)
def updateConvMemberByConvId(cur, conversation_id, user_id, data={}):
    try:
        for item in data.items():
            if item[0] in can_update_fields:
                cur.execute(
                    f"UPDATE conversation_members SET {item[0]}=%s WHERE conversation_id=%s AND user_id=%s",
                    (item[1], conversation_id, user_id)
                )
    except:
        return None


# 删除会话成员
def deleteConvMember(cur, conversation_id, user_id):
    cur.execute(
        "DELETE FROM conversation_members WHERE conversation_id=%s AND user_id=%s",
        (conversation_id, user_id)
    )


