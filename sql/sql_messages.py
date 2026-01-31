

def insert_message(cur, msgData):
    sql = """
    INSERT INTO messages (sender_id, conversation_id, content, type, status)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (
        msgData['sender_id'],
        msgData['convId'],
        msgData['content'],
        msgData['type'],
        msgData['status']
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