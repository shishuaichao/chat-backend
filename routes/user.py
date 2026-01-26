
from flask import Blueprint, jsonify

# 1. 创建蓝图（参数：蓝图名、模块名、URL前缀）
user_bp = Blueprint(
    "user",          # 蓝图唯一标识
    __name__,          # 当前模块名
    url_prefix="/user"  # 该蓝图下所有路由的统一前缀（可选，简化路由）
)


@user_bp.route('/registry', methods=['POST'])
def registry():
    return jsonify({'message': 'Registry success'}), 200    

@user_bp.route('/login', methods=['POST'])  
def login():
    return jsonify({'message': 'Login success'}), 200 
