
from flask import jsonify

def resJson(code, msg, data):
    return jsonify({
        "code": code, 
        "msg": msg, 
        "data": data
    }) 