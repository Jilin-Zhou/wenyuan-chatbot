# chatbot2024 Dockerfile - 知识库+大模型对话后端
# 多阶段构建，优化镜像大小

# ==================== 构建阶段 ====================
FROM python:3.10-slim as builder

WORKDIR /build

# 设置pip源
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_NO_CACHE_DIR=1

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --user -r requirements.txt
RUN pip install --user flask-cors

# ==================== 运行阶段 ====================
FROM python:3.10-slim as runtime

WORKDIR /app

# 从构建阶段复制依赖
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# 设置环境变量（运行时通过docker-compose或-e传入）
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# 复制应用代码
COPY app.py .
COPY gpt.py .
COPY chat/ ./chat/

# 创建static目录（用于存放数据库）
RUN mkdir -p /app/static

# 暴露端口
EXPOSE 1090

# 健康检查（使用简单的端口检查，避免触发embedding计算）
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 1090)); s.close()" || exit 1

# 启动应用
CMD ["python", "app.py", "--port", "1090"]