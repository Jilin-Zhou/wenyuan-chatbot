"""
使用BGE-small-zh模型生成embedding
本地运行，无需API密钥
"""
from sentence_transformers import SentenceTransformer
import numpy as np

# 加载本地模型（首次运行会自动下载，约33MB）
model = None

def get_model():
    """懒加载模型，避免启动时加载"""
    global model
    if model is None:
        print("正在加载BGE-small-zh模型...")
        model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
        print("模型加载完成！")
    return model

def get_embedding(text):
    """
    将文本转换为embedding向量
    
    Args:
        text: 输入文本
    
    Returns:
        numpy数组，维度为512
    """
    m = get_model()
    embedding = m.encode(text, normalize_embeddings=True)
    return embedding

def get_embeddings_batch(texts):
    """
    批量生成embedding（更高效）
    
    Args:
        texts: 文本列表
    
    Returns:
        numpy数组矩阵，每行是一个512维向量
    """
    m = get_model()
    embeddings = m.encode(texts, normalize_embeddings=True)
    return embeddings


if __name__ == '__main__':
    # 测试
    test_text = "北京有哪些特色美食？"
    embedding = get_embedding(test_text)
    print(f"文本: {test_text}")
    print(f"Embedding维度: {len(embedding)}")
    print(f"Embedding示例（前10个值）: {embedding[:10]}")