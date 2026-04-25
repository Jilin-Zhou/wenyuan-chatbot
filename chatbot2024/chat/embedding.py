import pandas as pd
import numpy as np
from openai import OpenAI
import sqlite3
import os
import time
client=OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")
client.base_url = os.getenv("OPENAI_BASE_URL")

if os.path.exists('QA.db'):
    os.remove('QA.db')
db_connect = sqlite3.connect('QA.db')

# 找到static文件夹中的Excel文件
excel_path = "static/"
for file_path in os.listdir("static"):
    if file_path.endswith(".xlsx") and not file_path.startswith("~"):
        excel_path += file_path
        break
print(f"Embedding '{excel_path}'")
sheets_dict = pd.read_excel(excel_path, sheet_name=None)
df = pd.concat(sheets_dict.values(), ignore_index=True)

print("df: ", df)
df.to_sql('QAEmbeddings', db_connect, if_exists='replace', index=False)
count = 0
embeddings = []
for question in df['questions']:
    response = client.embeddings.create(
        input=question,
        model="text-embedding-3-small"
    ).data[0].embedding
    embeddings.append(response)
    count += 1
    print("=", end="", flush=True)
    time.sleep(2)
print()

# 将嵌入向量存储到数据库中
db_connect.execute("ALTER TABLE QAEmbeddings ADD COLUMN embedding BLOB")
for i, embedding in enumerate(embeddings):
    embedding_string = np.array(embedding).tobytes()
    db_connect.execute("UPDATE QAEmbeddings SET embedding = ? WHERE rowid = ?", (embedding_string, i+1))
db_connect.commit()

# Query the database to verify that the embeddings have been saved correctly
cursor = db_connect.execute("SELECT embedding FROM QAEmbeddings LIMIT 1")
row = cursor.fetchone()
embedding_binary = row[0]
# 将二进制数据转换回numpy数组
embedding_array = np.frombuffer(embedding_binary, dtype=np.float64)
# 打印numpy数组
print(embedding_array)

# 关闭数据库连接
db_connect.close()



# # Save the modified DataFrame back to the Excel file
# df.to_excel('static/24OPENDAY.xlsx', index=False)
