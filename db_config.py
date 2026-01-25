# ---------------------- 1. 配置本地MySQL连接参数（改这4行！） ----------------------
MYSQL_CONFIG = {
    'host': 'localhost',      # 本地数据库地址，固定
    'port': 3306,             # 你的端口，固定3306
    'user': 'root',           # 你的MySQL用户名（比如root）
    'password': 'rootroot',     # 你的MySQL密码（必填！）
    'database': 'school',     # teacher表所在的数据库名（必填！）
    'charset': 'utf8mb4'      # 避免中文乱码，固定
}