

user_map = {'1': '7kZhWxOCOJ9JAOHXAAAB', '3': 'jk7AlLLn6mUTvqDtAAAD'}

members = [{'user_id': 1, 'unread_count': 97, 'last_read_msg_id': 285}, {'user_id': 3, 'unread_count': 96, 'last_read_msg_id': 267}]

for m in members:
    print(m['user_id'], user_map[str(m['user_id'])])