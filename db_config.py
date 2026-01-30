import pymysql

# ---------------------- 1. 配置本地MySQL连接参数（改这4行！） ----------------------
MYSQL_CONFIG = {
    'host': 'localhost',      # 本地数据库地址，固定
    'port': 3306,             # 你的端口，固定3306
    'user': 'root',           # 你的MySQL用户名（比如root）
    'password': 'rootroot',     # 你的MySQL密码（必填！）
    'database': 'chat',     # teacher表所在的数据库名（必填！）
    'charset': 'utf8mb4'      # 避免中文乱码，固定
}

# 数据库连接
def get_db():
    return pymysql.connect(
        host=MYSQL_CONFIG['host'],
        port=MYSQL_CONFIG['port'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
        database=MYSQL_CONFIG['database'],
        charset=MYSQL_CONFIG['charset'],
        cursorclass=pymysql.cursors.DictCursor
    )