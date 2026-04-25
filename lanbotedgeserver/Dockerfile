# lanbotedgeserver Dockerfile - 边缘服务器 + 机器人控制
# 注意：语音功能在Docker中受限，主要用于调试API和聊天功能

FROM python:3.10-slim

WORKDIR /app

# 设置pip源
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_NO_CACHE_DIR=1

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    # 网络工具
    curl \
    # YAML处理
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖（排除PyAudio等需要音频设备的包）
RUN pip install requests==2.27.1 \
    Flask==1.1.4 \
    flask-restplus==0.13.0 \
    werkzeug==0.16.1 \
    markupsafe==2.0.1 \
    websocket-client==1.3.3 \
    websocket-server==0.6.4 \
    PyYaml==6.0 \
    gevent==21.12.0 \
    gevent-websocket==0.10.1 \
    eel==0.15.3 \
    python-dotenv==1.0.0

# 复制应用代码
COPY edge_server/ ./edge_server/
COPY bin/ ./bin/
COPY resources/ ./resources/

# 设置环境变量
ENV PYTHONUNBUFFERED=1
# Docker中禁用语音功能
ENV VOICE_EN=false
ENV DOCKER_ENV=true
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=20550

# 暴露端口
EXPOSE 20550 20551

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:20550/api/config/default || exit 1

# 启动应用
CMD ["python", "edge_server/main.py"]