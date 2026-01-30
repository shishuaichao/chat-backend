from flask import Blueprint

# 创建蓝图（参数：蓝图名、模块名、URL前缀）
user_bp = Blueprint(
    "user",          # 蓝图唯一标识
    __name__,          # 当前模块名
    url_prefix="/user"  # 该蓝图下所有路由的统一前缀（可选，简化路由）
)

# 定义常量api并导出
class ApiUser:
    def __init__(self): 
        self.register = "/info/register"
        self.info = "/info/userInfo"
        self.update = "/info/updateInfo"

        self.friend_add = "/friend/addFriend"
        self.set_remark = "/friend/setRemark"
        self.friend_list = "/friend/friendList"
        self.friend_info = "/friend/friendInfo"
        self.friend_apply_list = "/friend/applyList"

        self.group_list = "/group/groupList"

api_user = ApiUser()
