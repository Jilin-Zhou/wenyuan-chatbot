# lanbot-front-chat Dockerfile - Vue 3 前端界面
# 多阶段构建：development 和 production

# ==================== 基础阶段 ====================
FROM node:18-alpine as base

WORKDIR /app

# 复制依赖文件
COPY package.json package-lock.json* ./

# ==================== 开发阶段 ====================
FROM base as development

# 安装所有依赖（包括devDependencies）
RUN npm install

# 复制源代码
COPY . .

# 暴露Vite开发服务器端口
EXPOSE 5173

# 启动开发服务器（支持热更新）
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ==================== 构建阶段 ====================
FROM base as build

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# ==================== 生产阶段 ====================
FROM nginx:alpine as production

# 复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]