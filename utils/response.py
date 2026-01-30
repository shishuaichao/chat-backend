
from flask import jsonify

def resJson(code, msg, data):
    return jsonify({
        "code": 200, 
        "msg": "注册成功", 
        "data": {"username": username, "nickname": nickname, "id": id}
    }) 