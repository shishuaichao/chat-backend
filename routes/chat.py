
from flask import Blueprint, jsonify
from wechat.operate import get_all_chats

# 1. 创建蓝图（参数：蓝图名、模块名、URL前缀）
chat_bp = Blueprint(
    "wechat",          # 蓝图唯一标识
    __name__,          # 当前模块名
    url_prefix="/chat"  # 该蓝图下所有路由的统一前缀（可选，简化路由）
)

# 2. 用蓝图装饰器定义路由（替代原有的@app.route）
@chat_bp.route('/records', methods=['GET'])
def get_chats():
    res = get_all_chats()
    return jsonify(res)
