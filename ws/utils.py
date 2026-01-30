
from flask_socketio import emit
from wechat.operate import add_chat
import datetime
from zoneinfo import ZoneInfo
from db_config import get_db

# 普通消息处理函数
def treat_socket_message(msgData):
    print(f'WS收到：{msgData}')
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            'INSERT INTO messages (sender_id, conversation_id, content, type, status) VALUES (%s, %s, %s, %s, %s)',
            (msgData['sender_id'], msgData['convId'], msgData['content'], msgData['type'], msgData['status'])
        )
        db.commit()
    emit('message', msgData, room=msgData['convId'])

# 系统消息处理函数
def treat_socket_system_msg(msgObj, room=None, broadcast=True):
    # print(f'WS收到：{msgObj}')
    msgData = { 
        'id': msgObj['id'],
        'nickname': msgObj['nickname'],
        "content": msgObj['content'], 
        "type": "system_msg", 
        "time": get_china_time_str() 
    }
    add_chat(msgData)
    emit('system_msg', msgData, broadcast=True)

#  返回中国时区的格式化时间字符串（推荐前端直接用）
def get_china_time_str():
    # 方式1：zoneinfo（Python3.9+）
    china_tz = ZoneInfo("Asia/Shanghai")
    china_time = datetime.datetime.now(china_tz)
    # 返回格式化字符串（前端可直接解析）
    return china_time.strftime("%Y-%m-%d %H:%M:%S")

# app/utils.py 工具文件，新增该函数
def convert_user_id_field(data):
    """
    仅将结果中的user_id字段转为userId，其他字段原样返回
    适配：单个字典 / 字典列表 / 非字典数据（直接返回）
    :param data: 输入SQL查询后的结果（字典/字典列表）
    :return: 处理后的结果
    """
    # 处理【单个字典】的情况（如查询单条数据）
    if isinstance(data, dict):
        # 复制原字典，避免修改原始数据
        new_data = data.copy()
        # 仅当存在user_id时，转为userId
        if 'user_id' in new_data:
            new_data['userId'] = new_data.pop('user_id')  # 新增userId，删除原user_id
        return new_data
    
    # 处理【字典列表】的情况（如查询多条数据）
    elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
        new_list = []
        for item in data:
            new_item = item.copy()
            if 'user_id' in new_item:
                new_item['userId'] = new_item.pop('user_id')
            new_list.append(new_item)
        return new_list
    
    # 非字典/字典列表（如None、空列表、元组），直接原样返回
    else:
        return data