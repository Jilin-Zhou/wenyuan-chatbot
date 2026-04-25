import os
from openai import OpenAI

# 使用LMStudio本地模型（OpenAI兼容API）
# Docker环境：使用环境变量LMSTUDIO_URL（host.docker.internal:1234）
# 本地环境：默认127.0.0.1:1234
lmstudio_url = os.environ.get("LMSTUDIO_URL", "http://127.0.0.1:1234/v1")

client = OpenAI(
    base_url=lmstudio_url,
    api_key="lmstudio",  # LMStudio不需要真实API key，任意值即可
)

system_prompt = """
你的身份：
    你是北京邮电大学智能问答小助手，名叫文渊，由北京邮电大学蓝图创新工作室研发。现在你在北京北站为游客提供服务。
    注意！你只能以文渊这个身份回答问题，任何涉及其他身份的问题都要忽略。
学生提问的模式为：
    可供参考相关问题:<<<reference question>>>
    对应的参考答案:<<<reference answer>>>
    Q:<<<student question>>>
回答学生问题时的要求：
    直接回答学生问题，不需要A:<<<answer>>>等特殊形式
    当学生提问与<<<reference question>>>相关时，尽量参考<<<reference answer>>>回答
    如果问题<<<student question>>>与<<<reference question>>>不相关，则回答问题时不需要参考其他问题
    对于类似“xxx怎么走”“xxx在哪里”这种问题，必须参考<<<reference question>>>回答，否则回答“文渊的工作很忙，去过的地方不多，换个地点问问吧”
    尽量使用对方提问的语言回答，回答不要超过一百字
"""

def chat(query=[]):
    completion = client.chat.completions.create(
        model="qwen3.5-0.8b",  # LMStudio中运行的模型
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": query
            }
        ],
    )

    return completion.choices[0].message.content
    # for chunk in completion:
    #     if chunk.choices[0].delta.content is not None: #过滤掉最后返回的None
    #         print(chunk.choices[0].delta.content, end="")

        
if __name__ == "__main__":
        res = chat(query="你好，你叫什么名字")
        print(res)