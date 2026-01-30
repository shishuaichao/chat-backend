from flask import Blueprint

# 1. 创建蓝图（参数：蓝图名、模块名、URL前缀）
chat_bp = Blueprint(
    "chat",          # 蓝图唯一标识
    __name__,          # 当前模块名
    url_prefix="/chat"  # 该蓝图下所有路由的统一前缀（可选，简化路由）
)

# 定义常量api并导出
class ApiChat:
    def __init__(self): 
        self.create_conv = "/conversation/createConversation"

api_chat = ApiChat()
