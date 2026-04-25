import sqlite3
import pandas as pd
import numpy as np
from chat.embedding_bge import get_embedding  # 使用本地BGE模型

# 连接到SQLite数据库
conn = sqlite3.connect('QA.db')

def calculate_cosine_similarity(vector1, vector2):
    # 计算两个向量的点积
    dot_product = np.dot(vector1, vector2)
    # 计算每个向量的L2范数（即向量的长度）
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)
    # 计算余弦相似度
    cosine_similarity = dot_product / (norm_vector1 * norm_vector2)
    return cosine_similarity

def most_sim_ques(query):
    # 使用本地BGE-small-zh模型生成embedding
    embedding = get_embedding(query)

    # 连接到SQLite数据库
    conn = sqlite3.connect('QA.db')
    cur = conn.cursor()

    # 查询所有的embedding
    cur.execute("SELECT embedding, questions, answers FROM QAEmbeddings")
    rows = cur.fetchall()

    # 计算余弦距离并找到最小的question
    max_similar = -1
    sim_ques = ""
    sim_ans=""
    for row in rows:
        db_embedding = np.frombuffer(row[0], dtype=np.float64)
        # print(len(db_embedding))
        # print(len(embedding))
        db_question = row[1]
        db_answers = row[2]
        similar = calculate_cosine_similarity(embedding, db_embedding)
        if similar > max_similar:
            max_similar = similar
            sim_ques = db_question
            sim_ans = db_answers

    print("similarity", max_similar)
    if max_similar>0.4:
        print("Question with minimum cosine distance:", sim_ques)
        print("Answer with minimum cosine distance:", sim_ans)
        return sim_ques,sim_ans
    return "无","无"
 

if __name__ == '__main__':
    most_sim_ques("恐龙是什么时候灭绝的")