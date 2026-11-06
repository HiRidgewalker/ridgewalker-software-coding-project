# 第 3 步：创建 FastAPI + React 示例项目

## 3.1 项目结构

```
jenkins-demo/                    # 项目根目录（也是 Git 仓库根目录）
├── backend/                     # FastAPI 后端
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py             # API 入口
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_main.py        # 后端测试
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/                    # React + Tailwind 前端
│   ├── src/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── tests/
│   │   └── App.test.jsx        # 前端测试
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── docker-compose.local.yml     # 本地运行用，直接 build 源码
├── docker-compose.yml           # Jenkins 部署用，引用已构建镜像
└── Jenkinsfile                  # Jenkins Pipeline 定义
```

## 3.2 创建后端（FastAPI）

### `backend/pyproject.toml`

```toml
[project]
name = "jenkins-demo-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi==0.115.0",
    "uvicorn[standard]==0.30.0",
]

[dependency-groups]
dev = [
    "pytest==8.3.0",
    "ruff==0.6.0",
]

[tool.uv]
package = false
```

创建或修改 `pyproject.toml` 后执行一次 `uv lock`，生成 `uv.lock`。这个锁文件必须提交到 Git 仓库，后面的 Jenkins Pipeline 会用 `uv sync --frozen` 按锁文件安装依赖。

### `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Jenkins Demo API")

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ITEMS = [
    {"id": 1, "name": "Learn Docker"},
    {"id": 2, "name": "Learn Jenkins"},
    {"id": 3, "name": "Learn CI/CD"},
]


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/items")
def get_items():
    return ITEMS


@app.get("/api/items/{item_id}")
def get_item(item_id: int):
    for item in ITEMS:
        if item["id"] == item_id:
            return item
    return {"error": "not found"}
```

### `backend/tests/test_main.py`

```python
from app.main import get_item, get_items, health


def test_health():
    assert health() == {"status": "ok"}


def test_get_items():
    data = get_items()
    assert len(data) == 3


def test_get_item():
    assert get_item(1)["name"] == "Learn Docker"


def test_get_item_not_found():
    assert get_item(999) == {"error": "not found"}
```

> 这里为了让入门流水线更稳定，测试直接调用 endpoint 函数。真实项目可以再增加 `fastapi.testclient.TestClient` 或 `httpx` 做 HTTP 层测试。

### `backend/Dockerfile`

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.4 /uv /uvx /usr/local/bin/

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 安装依赖（分层缓存优化）
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 3.3 创建前端（React + Tailwind）

### 初始化前端项目

```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install -D tailwindcss @tailwindcss/vite
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

执行完 `npm install` 后会生成 `package-lock.json`。这个文件必须提交到 Git 仓库，因为后面的 Dockerfile 和 Jenkins Pipeline 会使用 `npm ci`，而 `npm ci` 要求项目中存在锁文件。

### `frontend/vite.config.js`

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const apiProxyTarget = process.env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:8001'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: apiProxyTarget,
        changeOrigin: true,
        secure: false,
      },
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.js',
  },
})
```

### `frontend/tests/setup.js`

```js
import '@testing-library/jest-dom'
```

### `frontend/src/App.jsx`

```jsx
import { useState, useEffect } from 'react'

function App() {
  const [items, setItems] = useState([])
  const [health, setHealth] = useState('')

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setHealth(data.status))
      .catch(() => setHealth('unreachable'))

    fetch('/api/items')
      .then(res => res.json())
      .then(data => setItems(data))
      .catch(() => setItems([]))
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-4 text-center">Jenkins CI/CD Demo</h1>

        <div className="mb-4 p-3 bg-green-50 rounded text-center">
          Backend: <span className="font-mono font-bold">{health || 'loading...'}</span>
        </div>

        <ul className="space-y-2">
          {items.map(item => (
            <li key={item.id} className="p-3 bg-gray-50 rounded flex justify-between">
              <span className="text-gray-500">#{item.id}</span>
              <span className="font-medium">{item.name}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default App
```

### `frontend/tests/App.test.jsx`

```jsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import App from '../src/App'

// Mock fetch
global.fetch = vi.fn((url) => {
  if (url === '/api/health') {
    return Promise.resolve({ json: () => Promise.resolve({ status: 'ok' }) })
  }
  if (url === '/api/items') {
    return Promise.resolve({
      json: () => Promise.resolve([
        { id: 1, name: 'Learn Docker' },
        { id: 2, name: 'Learn Jenkins' },
      ])
    })
  }
  return Promise.reject(new Error('not found'))
})

describe('App', () => {
  it('renders the title', async () => {
    render(<App />)
    await waitFor(() => {
      expect(screen.getByText('Jenkins CI/CD Demo')).toBeInTheDocument()
    })
  })

  it('shows backend health status', async () => {
    render(<App />)
    await waitFor(() => {
      expect(screen.getByText('ok')).toBeInTheDocument()
    })
  })
})
```

### `frontend/Dockerfile`

```dockerfile
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
    location / { root /usr/share/nginx/html; try_files $$uri /index.html; } \
    location /api/ { proxy_pass http://backend:8000/api/; } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
```

## 3.4 docker-compose.local.yml（本地验证用）

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

这个 compose 文件用于本地手动验证，直接从 `backend/` 和 `frontend/` 构建镜像。

再创建 Jenkins 部署用的 `docker-compose.yml`：

```yaml
services:
  backend:
    image: jenkins-demo-backend:${BACKEND_TAG:-latest}
    ports:
      - "8000:8000"

  frontend:
    image: jenkins-demo-frontend:${FRONTEND_TAG:-latest}
    ports:
      - "3000:80"
    depends_on:
      - backend
```

第 4 步的 Jenkins Pipeline 会先执行 `docker build -t jenkins-demo-backend:${BUILD_NUMBER}`，再通过 `BACKEND_TAG=${BUILD_NUMBER}` 让 compose 使用刚构建好的镜像。

## 3.5 本地验证

```bash
# 在项目根目录下
docker compose -f docker-compose.local.yml up -d --build

# 验证后端
curl http://localhost:8000/api/health
# → {"status":"ok"}

# 验证前端
# 浏览器打开 http://localhost:3000
# 应该能看到后端状态 "ok" 和 item 列表
```

### 本地跑测试

```bash
# 后端测试
cd backend
uv sync
uv run pytest tests/ -v

# 前端测试
cd frontend
npm install
npx vitest run
```

## 3.6 Jenkinsfile

本仓库的 `jenkins-demo/Jenkinsfile` 已经提供了一份可以直接实践的 Pipeline。它会执行：

```text
Checkout
  -> Backend Lint & Test
  -> Frontend Test
  -> Build Images
  -> Deploy
```

如果你是从零创建项目，请在项目根目录创建 `Jenkinsfile`，内容见第 4 步。

---

**下一步**：[04-jenkins-pipeline.md](./04-jenkins-pipeline.md) — 编写 Jenkins Pipeline
