from volcengine.ark import Ark
from volcengine.ark.types import ChatCompletionRequest, Message

# 1. 初始化客户端（替换为你的 API Key/Secret Key）
client = Ark(
    api_key="27d8e23b-9131-4391-9c4f-fd0ae704c618",
    secret_key="TjJNeE5XTmtZVE0yT1RnM05HVmpPV0psTURkaFpUQm1aV1F4WVdJNE5qQQ=="
)

# 2. 定义聊天函数（支持多轮上下文）
def chat_with_douban(messages):
    """
    调用豆包 API 实现聊天
    :param messages: 对话上下文列表，格式：[{"role": "user/assistant", "content": "消息内容"}]
    :return: 豆包的回复内容
    """
    try:
        # 构造请求参数
        request = ChatCompletionRequest(
            model="doubao-3.5",  # 豆包模型版本（可选 doubao-4/doubao-3.5）
            messages=[Message(**msg) for msg in messages],
            temperature=0.7,  # 随机性（0-1，值越高回复越灵活）
            max_tokens=1000  # 最大回复字数
        )
        # 调用 API 并获取回复
        response = client.chat.completions.create(request)
        return response.choices[0].message.content
    except Exception as e:
        return f"调用失败：{str(e)}"