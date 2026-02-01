
dic = {
    "sss": 1,
    "aaa": 2
}

for item in dic.keys():
    print(item)
    print(dic[item])

# dic = {"name": "张三", "age": 20, "gender": "男"}

# # 1. 遍历键（默认，等价于 for k in dic.keys()）
# for k in dic:
#     print(f"键：{k}")  # 输出：name age gender

# # 2. 遍历值
# for v in dic.values():
#     print(f"值：{v}")  # 输出：张三 20 男