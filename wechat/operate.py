# 导入依赖 + 导入配置文件
import pymysql
from db_config import MYSQL_CONFIG  # 引用同目录的db_config.py中的配置

# db_operation.py 新增函数
def add_chat(d):
    if 'content' not in d or 'type' not in d or 'time' not in d:
        print("新增聊天失败：缺失字段")
        return
    valid_fields = {"content", "type", "time", "id", "nickname", "avatar"}
    # if not valid_fields.issubset(d.keys()):
    #     print("新增聊天失败：包含无效字段")
    #     return
    
    filtered_data = {k: v for k, v in d.items() if k in valid_fields and v is not None}
    fields = ", ".join(filtered_data.keys())
    # 占位符：如 "%s, %s"（MySQL 占位符）
    placeholders = ", ".join(["%s"] * len(filtered_data))
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        # 执行插入SQL
        cursor.execute(f'INSERT INTO wechat ({fields}) VALUES ({placeholders})', tuple(filtered_data.values()))
        # cursor.execute('INSERT INTO wechat () VALUES (%s, %s, %s, %s, %s, %s)', (d['id'], d['nickname'], d['avatar'], d['content'], d['type'], d['time']))
        conn.commit()  # 写操作必须commit
        print("新增聊天成功！")
    except Exception as e:
        conn.rollback()  # 出错回滚
        print(f"新增失败：{e}")
    finally:
        cursor.close()
        conn.close()
     

