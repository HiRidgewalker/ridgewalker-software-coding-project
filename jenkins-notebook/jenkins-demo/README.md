# jenkins-demo

FastAPI + React 示例项目，配合 JenkinsPipeline 教程使用。

## 目录结构

```
jenkins-demo/
├── backend/          # FastAPI 后端
├── frontend/         # React + Vite + Tailwind 前端
├── docker-compose.local.yml  # 本地 build 验证
├── docker-compose.yml        # Jenkins 使用已构建镜像部署
└── Jenkinsfile
```

## 本地运行

```bash
docker compose -f docker-compose.local.yml up -d --build
```

- 前端：http://localhost:3000
- 后端：http://localhost:8000/api/health

## 本地测试

```bash
# 后端
cd backend
uv sync
uv run pytest tests/ -v

# 后端开发服务
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001

# 前端
cd frontend
npm install
npx vitest run
npm run dev
```

前端开发服务器会把 `/api` 代理到 `http://127.0.0.1:8001`。如果后端运行在其他端口，可以覆盖代理目标：

```bash
VITE_API_PROXY_TARGET=http://127.0.0.1:8000 npm run dev
```

## 详细说明

参考 [JenkinsNotebook/03-sample-project.md](../JenkinsNotebook/03-sample-project.md) 与
[JenkinsNotebook/04-jenkins-pipeline.md](../JenkinsNotebook/04-jenkins-pipeline.md)。
