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
