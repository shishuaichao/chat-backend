

def insert_message(cur, msgData):
    # userId // 发送者id
    # content // 消息内容
    # msgType // 消息类型 1: 文本 2: 图片 3: 语音 4: 视频 5: 文件 6: 位置 7: 链接 8: 系统消息
    # convId // 会话id
    # convType  // 会话类型 1: 单聊 2: 群聊
    # to  // 单聊接收者id
    sql = """
    INSERT INTO messages (sender_id, conversation_id, content, type)
    VALUES (%s, %s, %s, %s)
    """
    values = (
        msgData['userId'],
        msgData['convId'],
        msgData['content'],
        msgData['msgType'],
    )
    cur.execute(sql, values)
    return cur.lastrowid

def get_message(cur, msg_id):
    sql = """
    SELECT * FROM messages WHERE id = %s
    """
    values = (msg_id,)
    cur.execute(sql, values)
    return cur.fetchone()

# 获取对应会话中的所有聊天记录
def get_messages_records(cur, conv_id):
    sql = """
    SELECT * FROM messages WHERE conversation_id=%s
    """
    values = (conv_id,)
    cur.execute(sql, values)
    return cur.fetchall()

# 获取会话中所有成员的未读信息列表
def getConvMemberUnreadInfoList(cur, conv_id, last_read_msg_id):
    print('getConvMemberUnreadInfoList', conv_id, last_read_msg_id)
    sql = """
    SELECT * FROM messages WHERE conversation_id=%s AND id > %s
    """
    values = (conv_id, last_read_msg_id)
    cur.execute(sql, values)
    return cur.fetchall()

# 获取会话中最后一条信息
def getLastMessage(cur, conv_id):
    sql = """
    SELECT * FROM messages WHERE conversation_id=%s ORDER BY id DESC LIMIT 1
    """
    values = (conv_id,)
    cur.execute(sql, values)
    return cur.fetchone()
