
from flask_socketio import emit
from wechat.operate import add_chat
import datetime
from zoneinfo import ZoneInfo

# 普通消息处理函数
def treat_socket_message(msgObj):
    print(f'WS收到：{msgObj}')
    msg = msgObj['content']
    if msg.startswith("群公告~~"):
        msgData = { 
            "content": msgObj['content'].replace("群公告~~", ""), 
            "type": "system_msg", 
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        }
        add_chat(msgData)
        emit('system_msg', msgData, broadcast=True)
        return
    msgData = { 
        'id': msgObj['id'],
        'nickname': msgObj['nickname'],
        "content": msgObj['content'], 
        "avatar": msgObj['avatar'], 
        "type": "message", 
        "time": get_china_time_str()
    }
    add_chat(msgData)
    emit('message', msgData, broadcast=True)
    print('get_china_time_str()', get_china_time_str())

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