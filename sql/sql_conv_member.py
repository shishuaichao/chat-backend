

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

# 查询单个成员的信息
def getConvMemberUnreadInfo(cur, conversation_id, user_id):
    cur.execute(
        "SELECT * FROM conversation_members WHERE conversation_id=%s AND user_id=%s",
        (conversation_id, user_id)
    )
    return cur.fetchone()

# 更新会话中成员的未读id
def updateConvMemberUnreadInfo(cur, conversation_id, user_id, last_read_msg_id):
    cur.execute(
        "UPDATE conversation_members SET last_read_msg_id=%s WHERE conversation_id=%s AND user_id=%s   ",
        (last_read_msg_id, conversation_id, user_id)
    )


# 获取未读数量
def getUnreadCountBylastReadMsgId(cur, conversation_id, user_id, last_read_msg_id):
    cur.execute(
        "SELECT * FROM conversation_members  WHERE conversation_id=%s AND user_id=%s AND last_read_msg_id>%s",
        (conversation_id, user_id, last_read_msg_id)
    )
    return len(cur.fetchall())



# 更新未读数量
def updateConvMemberUnreadCount(cur, conversation_id, user_id, unread_count):
    cur.execute(
        "UPDATE conversation_members SET unread_count=%s WHERE conversation_id=%s AND user_id=%s",
        (unread_count, conversation_id, user_id)
    )
    member_info = getConvMemberUnreadInfo(cur, conversation_id, user_id)
    unread_count = member_info['unread_count'] + 1

# 查询会话中所有成员的信息
def getConvMembersInfo(cur, conversation_id):
    cur.execute(
        "SELECT user_id, unread_count, last_read_msg_id FROM conversation_members WHERE conversation_id=%s",
        (conversation_id,)
    )
    return cur.fetchall()