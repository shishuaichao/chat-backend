
from .chat import chat_bp
from .user import user_bp

# 导出所有蓝图，方便主app批量注册
all_blueprints = [chat_bp, user_bp]
