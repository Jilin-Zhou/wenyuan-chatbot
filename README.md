# 文渊智能问答机器人

机器人维修。

## 项目简介

本项目是一个完整的智能问答机器人系统，采用前后端分离架构：

- **chatbot2024**: Python Flask 后端，知识库检索 + 大模型对话
- **lanbotedgeserver**: 边缘服务器，机器人控制 + 语音交互
- **lanbot-front-chat**: Vue 3 前端界面

### 技术特点

- ✅ **完全本地化部署**：无需依赖云端 API
- ✅ **本地 Embedding**：使用 BGE-small-zh-v1.5 替代 OpenAI Embedding
- ✅ **本地大模型**：使用 LMStudio 运行 Qwen3.5-0.8b
- ✅ **Docker 容器化**：一键部署，环境隔离
- ✅ **知识库问答**：基于向量检索的 RAG 架构

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户界面 (Vue 3)                        │
│                    http://localhost:5173                     │
└─────────────────────────┬───────────────────────────────────┘
                          │ WebSocket (20551)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    边缘服务器 (Python)                        │
│              http://localhost:20550 / 20551                  │
│              机器人控制 + 语音交互 + WebSocket                │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP (1090)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  对话后端 (Python Flask)                      │
│                    http://localhost:1090                     │
│              知识库检索 + 大模型对话生成                       │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP API
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   LMStudio (本地运行)                         │
│                  http://localhost:1234                       │
│              Qwen3.5-0.8b 大模型服务                          │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 方式一：Docker 部署（推荐）

#### 1. 前置准备

**安装 LMStudio 并下载模型：**

1. 下载安装 [LMStudio](https://lmstudio.ai/)
2. 在 LMStudio 中搜索并下载 `Qwen3.5-0.8b` 模型
3. 启动本地服务器：
   - 点击左侧 "Local Server" 标签
   - 选择已下载的 Qwen 模型
   - 点击 "Start Server"，端口设为 `1234`

**安装 Docker：**

- Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Linux: `sudo apt install docker-compose`

#### 2. 克隆项目

```bash
git clone https://github.com/Jilin-Zhou/wenyuan-chatbot.git
cd wenyuan-chatbot
```

#### 3. 启动服务

```bash
# 启动所有容器
docker-compose -p wenyuan up -d --build

# 查看容器状态
docker ps

# 查看日志
docker-compose -p wenyuan logs -f
```

#### 4. 访问系统

打开浏览器访问：http://localhost:5173

#### 5. 常用命令

```bash
# 停止所有容器
docker-compose -p wenyuan down

# 重启单个容器
docker restart wenyuan-chatbot
docker restart wenyuan-edge-server
docker restart wenyuan-frontend

# 查看容器日志
docker logs -f wenyuan-chatbot
docker logs -f wenyuan-edge-server
docker logs -f wenyuan-frontend

# 清理 Docker 资源（慎用）
docker system prune -a --volumes
```

---

### 方式二：直接部署

#### 1. 前置准备

**安装依赖：**

- Python 3.10+
- Node.js 18+
- LMStudio（同 Docker 部署）

#### 2. 克隆项目

```bash
git clone https://github.com/Jilin-Zhou/wenyuan-chatbot.git
cd wenyuan-chatbot
```

#### 3. 部署 chatbot2024（对话后端）

```bash
cd chatbot2024

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install flask-cors

# 设置环境变量
# Windows PowerShell:
$env:LMSTUDIO_URL = "http://127.0.0.1:1234/v1"
# Linux/Mac:
export LMSTUDIO_URL="http://127.0.0.1:1234/v1"

# 启动服务
python app.py
```

服务地址：http://localhost:1090

#### 4. 部署 lanbotedgeserver（边缘服务器）

```bash
cd lanbotedgeserver

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install requests==2.27.1
pip install Flask==1.1.4 flask-restplus==0.13.0
pip install werkzeug==0.16.1 markupsafe==2.0.1
pip install websocket-client==1.3.3 websocket-server==0.6.4
pip install PyYaml==6.0
pip install gevent==21.12.0 gevent-websocket==0.10.1
pip install eel==0.15.3
pip install python-dotenv==1.0.0

# 设置环境变量
# Windows PowerShell:
$env:CHATIE_API_URL = "http://127.0.0.1:1090/chatbot/api/v1.0/get"
$env:CHAT_CONF_NAME = "default"
$env:VOICE_EN = "false"
$env:BOT_TYPE = "SMART"

# 启动服务
python edge_server/main.py
```

服务地址：http://localhost:20550, WebSocket: ws://localhost:20551

#### 5. 部署 lanbot-front-chat（前端）

```bash
cd lanbot-front-chat

# 安装依赖
npm install

# 开发模式启动
npm run dev
```

前端地址：http://localhost:5173

---

## 知识库管理

### 添加问答数据

将 Excel 文件放入 `chatbot2024/static/` 目录，格式如下：

| 问题 | 答案 |
|------|------|
| 北京北站在哪里？ | 北京北站位于北京市海淀区... |
| ... | ... |

运行导入脚本：

```bash
cd chatbot2024
python chat/api.py  # 自动导入 Excel 数据
```

### 重新生成向量

如果更换了 Embedding 模型，需要重新生成向量：

```bash
cd chatbot2024
python regenerate_embeddings.py
```

---

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `LMSTUDIO_URL` | LMStudio API 地址 | `http://127.0.0.1:1234/v1` |
| `CHATIE_API_URL` | chatbot API 地址 | `http://chatbot:1090/...` |
| `CHAT_CONF_NAME` | 配置名称 | `default` |
| `VOICE_EN` | 是否启用语音 | `false` |
| `BOT_TYPE` | 机器人类型 | `SMART` |

### Docker 端口映射

| 服务 | 容器端口 | 主机端口 |
|------|----------|----------|
| chatbot | 1090 | 1090 |
| edge-server | 20550 | 20550 |
| edge-server (WS) | 20551 | 20551 |
| frontend | 5173 | 5173 |

---

## 项目结构

```
wenyuan-chatbot/
├── docker-compose.yml          # Docker Compose 配置
├── .env.example                # 环境变量示例
├── README.md                   # 项目说明
│
├── chatbot2024/                # 对话后端
│   ├── app.py                  # Flask 主程序
│   ├── gpt.py                  # LMStudio API 调用
│   ├── chat/
│   │   ├── api.py              # 问答 API
│   │   ├── embedding_bge.py    # BGE Embedding
│   │   └── query.py            # 知识库检索
│   ├── static/                 # 知识库数据目录
│   │   └── QA.db               # SQLite 数据库
│   ├── requirements.txt        # Python 依赖
│   └── Dockerfile
│
├── lanbotedgeserver/           # 边缘服务器
│   ├── edge_server/
│   │   ├── main.py             # 主程序
│   │   ├── bot/                # 机器人控制
│   │   ├── voice/              # 语音交互
│   │   ├── xunfei/             # 讯飞 SDK
│   │   └── web/                # WebSocket 服务
│   ├── resources/              # 配置文件
│   │   └── config/
│   │       └── default.yaml    # 机器人配置
│   ├── bin/                    # SDK 库文件
│   ├── requirements.txt        # Python 依赖
│   └── Dockerfile
│
└── lanbot-front-chat/          # Vue 前端
    ├── src/
    │   ├── views/
    │   │   ├── ChatView.vue    # 聊天界面
    │   │   └── voice.vue       # 语音界面
    │   ├── hooks/
    │   │   └── websocket.js    # WebSocket 连接
    │   └── configs/
    │       └── index.js        # 前端配置
    ├── package.json            # Node 依赖
    ├── vite.config.js          # Vite 配置
    └── Dockerfile
```

---

## 常见问题

### Q: LMStudio 连接失败？

确保 LMStudio 服务已启动：
- 打开 LMStudio → Local Server
- 确认模型已加载
- 确认端口为 1234
- 测试：`curl http://127.0.0.1:1234/v1/models`

### Q: Docker 容器无法访问 LMStudio？

Docker 内部使用 `host.docker.internal` 访问宿主机：
- Windows/Mac: 自动支持
- Linux: 需添加 `--add-host=host.docker.internal:host-gateway`

### Q: 前端无法连接 WebSocket？

检查 edge-server 是否正常运行：
```bash
docker logs wenyuan-edge-server
```

确认 WebSocket 端口 20551 已开放。

### Q: 如何更换大模型？

在 LMStudio 中加载其他模型（如 Qwen2.5、DeepSeek 等），重启服务即可。

---

## 技术栈

| 模块 | 技术 |
|------|------|
| 后端 | Python 3.10, Flask |
| 前端 | Vue 3, Vite |
| Embedding | BGE-small-zh-v1.5 (BAAI) |
| 大模型 | Qwen3.5-0.8b (LMStudio) |
| 容器化 | Docker, Docker Compose |
| 数据库 | SQLite |

---

## 许可证

MIT License

---

## 作者

北京北站文渊机器人项目组
