# ---- 构建阶段 ----
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---- 运行阶段 ----
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

# 添加 nginx 配置，将 /api 请求代理到后端
RUN echo 'server { \
    listen 80; \
    location / { root /usr/share/nginx/html; try_files $uri /index.html; } \
    location /api/ { proxy_pass http://backend:8000/api/; } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
