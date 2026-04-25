from openai import OpenAI
import os

client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")
client.base_url = os.getenv("OPENAI_BASE_URL")

# 假设你有一个原始问题和一些相关问题
original_question = "What is the capital of France?"


# 构建上下文字符串
context = f"Q:{sim_ques}\nA:{sim_ans}\n"

# 将原始问题附加到上下文字符串的末尾
prompt = context + f"Q:{original_question}\nA:"

# 使用这个提示字符串来查询模型
response = client.chat(models="gpt-3.5-turbo", messages=[{"role": "system", "content": prompt}])

# 打印模型的回答
print(response['choices'][0]['message']['content'])