# Docker 调试指南

> 更新日期：2026年4月25日
> 项目：文渊机器人智能问答系统

---

## 一、Docker环境概述

### 1.1 服务架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Docker Compose 服务架构                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────────┐                                               │
│   │   frontend      │  端口: 5173                                   │
│   │   (Vue 3)       │  → Vite开发服务器                              │
│   └─────────────────┘                                               │
│          │                                                          │
│          │ HTTP/WebSocket                                           │
│          ▼                                                          │
│   ┌─────────────────┐                                               │
│   │   edge-server   │  端口: 20550 (HTTP) / 20551 (WS)              │
│   │   (Python)      │  → 边缘服务器                                  │
│   └─────────────────┘                                               │
│          │                                                          │
│          │ HTTP                                                     │
│          ▼                                                          │
│   ┌─────────────────┐                                               │
│   │   chatbot       │  端口: 1090                                   │
│   │   (Flask)       │  → 知识库+大模型对话                           │
│   └─────────────────┘                                               │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    wenyuan-network                           │   │
│   │                    (Docker内部网络)                           │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 服务依赖关系

```
frontend → edge-server → chatbot → OpenAI API
```

---

## 二、快速启动

### 2.1 准备工作

#### 步骤1：创建环境变量文件

```powershell
# 进入项目目录
cd "e:\组里的项目"

# 复制环境变量模板
Copy-Item .env.example .env

# 编辑.env文件，填写API密钥
notepad .env
```

**必须配置的环境变量**：
```env
OPENAI_API_KEY=sk-your-actual-api-key
OPENAI_BASE_URL=https://api.openai.com/v1  # 或代理地址
```

#### 步骤2：检查Docker环境

```powershell
# 检查Docker是否运行
docker --version
docker-compose --version

# 如果未安装，请先安装Docker Desktop
```

### 2.2 启动所有服务

```powershell
# 进入项目目录
cd "e:\组里的项目"

# 启动所有服务（首次启动会构建镜像）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 2.3 验证服务

| 服务 | 测试地址 | 预期结果 |
|------|----------|----------|
| chatbot | `http://localhost:1090/chatbot/api/v1.0/get?question=你好` | 返回AI回答 |
| edge-server | `http://localhost:20550/api/voice/ask?question=test` | 返回 `{ok: true}` |
| frontend | `http://localhost:5173` | 显示聊天界面 |

---

## 三、调试命令

### 3.1 服务管理

```powershell
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启单个服务
docker-compose restart chatbot

# 查看服务状态
docker-compose ps

# 查看资源使用
docker stats
```

### 3.2 日志查看

```powershell
# 查看所有日志
docker-compose logs

# 查看特定服务日志
docker-compose logs chatbot
docker-compose logs edge-server
docker-compose logs frontend

# 实时跟踪日志
docker-compose logs -f chatbot

# 查看最近100行日志
docker-compose logs --tail=100 chatbot
```

### 3.3 进入容器调试

```powershell
# 进入chatbot容器
docker-compose exec chatbot bash

# 进入edge-server容器
docker-compose exec edge-server bash

# 进入frontend容器
docker-compose exec frontend sh

# 在容器内执行Python命令
docker-compose exec chatbot python -c "print('test')"

# 在容器内执行测试
docker-compose exec chatbot python test_db.py
```

### 3.4 重新构建

```powershell
# 重新构建所有镜像
docker-compose build

# 重新构建单个服务
docker-compose build chatbot

# 强制重新构建（不使用缓存）
docker-compose build --no-cache

# 重新构建并启动
docker-compose up -d --build
```

---

## 四、开发调试模式

### 4.1 源代码热更新

Docker配置已挂载源代码目录，修改代码后会自动生效：

| 服务 | 挂载目录 | 热更新支持 |
|------|----------|------------|
| chatbot | `./chatbot2024:/app` | 需重启容器 |
| edge-server | `./lanbotedgeserver/edge_server:/app/edge_server` | 需重启容器 |
| frontend | `./lanbot-front-chat/src:/app/src` | ✅ Vite自动刷新 |

**重启单个服务使代码生效**：
```powershell
docker-compose restart chatbot
docker-compose restart edge-server
```

### 4.2 调试Python服务

#### 方法1：进入容器调试

```powershell
# 进入chatbot容器
docker-compose exec chatbot bash

# 在容器内运行Python交互式调试
python -i
>>> from gpt import chat
>>> chat("你好")
```

#### 方法2：使用VS Code远程调试

1. 安装VS Code扩展：`Docker` 和 `Python`
2. 在容器中安装debugpy：
   ```powershell
   docker-compose exec chatbot pip install debugpy
   ```
3. 修改代码添加调试端口
4. 使用VS Code附加到容器

### 4.3 调试前端服务

```powershell
# 进入前端容器
docker-compose exec frontend sh

# 查看Vite配置
cat vite.config.js

# 查看环境变量
env | grep VITE
```

---

## 五、常见问题排查

### 5.1 服务无法启动

#### 问题：chatbot启动失败

```powershell
# 查看详细错误日志
docker-compose logs chatbot

# 可能原因：
# 1. API密钥无效 → 检查.env文件
# 2. 网络无法访问OpenAI → 配置代理地址
# 3. 数据库不存在 → 需要先构建知识库
```

**解决方案**：
```powershell
# 检查环境变量
docker-compose exec chatbot env | grep OPENAI

# 测试API连接
docker-compose exec chatbot python -c "
import os
from openai import OpenAI
client = OpenAI()
print(client.models.list())
"
```

#### 问题：edge-server无法连接chatbot

```powershell
# 检查网络连接
docker-compose exec edge-server ping chatbot

# 检查API地址配置
docker-compose exec edge-server env | grep CHATIE
```

**解决方案**：
- 确保使用Docker内部服务名：`http://chatbot:1090`
- 不要使用`localhost`或`127.0.0.1`

### 5.2 前端无法连接后端

#### 问题：WebSocket连接失败

**检查前端配置**：
```powershell
# 查看WebSocket地址配置
docker-compose exec frontend cat /app/src/configs/index.js
```

**解决方案**：
- Docker环境使用：`ws://localhost:20551`
- 确保edge-server WebSocket端口正确映射

#### 问题：CORS错误

已在chatbot2024添加CORS支持，如果仍有问题：

```powershell
# 检查CORS配置
docker-compose exec chatbot python -c "
from flask_cors import CORS
print('CORS installed')
"
```

### 5.3 数据库问题

#### 问题：QA.db不存在

```powershell
# 检查数据库文件
docker-compose exec chatbot ls -la /app/static/

# 如果不存在，需要构建
# 方法1：在本地构建后挂载
cd chatbot2024
python chat/embedding.py

# 方法2：在容器内构建
docker-compose exec chatbot python chat/embedding.py
```

### 5.4 端口冲突

#### 问题：端口被占用

```powershell
# 检查端口占用
netstat -ano | findstr :1090
netstat -ano | findstr :20550
netstat -ano | findstr :5173

# 解决方案：修改docker-compose.yml中的端口映射
```

---

## 六、进阶调试技巧

### 6.1 网络调试

```powershell
# 查看Docker网络
docker network ls
docker network inspect wenyuan-network

# 测试服务间连接
docker-compose exec edge-server curl http://chatbot:1090/chatbot/api/v1.0/get?question=test
```

### 6.2 性能调试

```powershell
# 查看资源使用
docker stats --no-stream

# 查看容器进程
docker-compose exec chatbot ps aux
```

### 6.3 数据持久化

```powershell
# 查看挂载卷
docker volume ls

# 备份数据库
docker-compose exec chatbot cp /app/static/QA.db /app/static/QA.db.backup

# 导出日志
docker-compose logs > debug-logs.txt
```

---

## 七、生产环境部署

### 7.1 构建生产镜像

```powershell
# 构建前端生产版本
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
```

### 7.2 环境变量管理

生产环境建议：
- 使用 secrets 管理API密钥
- 不要在.env文件中存储敏感信息
- 使用环境变量注入

---

## 八、调试流程图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Docker调试流程                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. 准备环境                                                        │
│     ├── 配置 .env 文件                                              │
│     └── 检查 Docker 环境                                            │
│                                                                     │
│  2. 启动服务                                                        │
│     ├── docker-compose up -d                                        │
│     └── docker-compose ps（检查状态）                                │
│                                                                     │
│  3. 验证服务                                                        │
│     ├── 测试 chatbot API                                            │
│     ├── 测试 edge-server API                                        │
│     └── 打开前端页面                                                │
│                                                                     │
│  4. 问题排查                                                        │
│     ├── 查看日志: docker-compose logs                               │
│     ├── 进入容器: docker-compose exec                               │
│     └── 检查网络: docker network inspect                            │
│                                                                     │
│  5. 代码调试                                                        │
│     ├── 修改源代码                                                  │
│     ├── 重启容器: docker-compose restart                            │
│     └── 查看效果                                                    │
│                                                                     │
│  6. 清理环境                                                        │
│     ├── docker-compose down                                         │
│     └── docker-compose down -v（删除卷）                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 九、命令速查表

| 场景 | 命令 |
|------|------|
| 启动服务 | `docker-compose up -d` |
| 停止服务 | `docker-compose down` |
| 查看状态 | `docker-compose ps` |
| 查看日志 | `docker-compose logs -f` |
| 重启服务 | `docker-compose restart <service>` |
| 进入容器 | `docker-compose exec <service> bash` |
| 重新构建 | `docker-compose build --no-cache` |
| 查看网络 | `docker network inspect wenyuan-network` |
| 清理所有 | `docker-compose down -v --rmi all` |

---

> 如有问题，请参考项目维护报告或联系开发人员