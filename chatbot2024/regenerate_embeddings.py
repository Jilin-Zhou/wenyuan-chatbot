"""
重新生成数据库embedding（使用BGE-small-zh）
运行此脚本将数据库中的OpenAI embedding替换为本地模型embedding
"""
import sqlite3
import numpy as np
from chat.embedding_bge import get_embeddings_batch
import os

def regenerate_embeddings(db_path='QA.db'):
    """
    重新生成数据库中所有问题的embedding
    """
    print("=" * 50)
    print("开始重新生成数据库embedding...")
    print("=" * 50)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 获取所有问题和答案
    cur.execute("SELECT rowid, questions, answers FROM QAEmbeddings")
    rows = cur.fetchall()
    
    if not rows:
        print("数据库中没有数据！")
        return
    
    print(f"找到 {len(rows)} 条问答数据")
    
    # 批量生成embedding
    questions = [row[1] for row in rows]
    print("正在批量生成embedding...")
    embeddings = get_embeddings_batch(questions)
    
    # 更新数据库
    print("正在更新数据库...")
    for i, row in enumerate(rows):
        id_ = row[0]
        embedding_bytes = embeddings[i].astype(np.float64).tobytes()
        cur.execute(
            "UPDATE QAEmbeddings SET embedding = ? WHERE rowid = ?",
            (embedding_bytes, id_)
        )
    
    conn.commit()
    conn.close()
    
    print("=" * 50)
    print("✅ Embedding重新生成完成！")
    print(f"新embedding维度: {len(embeddings[0])}")
    print("=" * 50)


if __name__ == '__main__':
    # 检查数据库是否存在
    db_path = 'QA.db'
    if not os.path.exists(db_path):
        print(f"错误：数据库文件 {db_path} 不存在！")
        print("请确保数据库文件在当前目录下")
    else:
        regenerate_embeddings(db_path)