# learning-langchain-notebook

一个面向工程实践的 LangChain 与 LangGraph 学习仓库。目录分成两条主线：

- `docs/langchain-langgraph/`：按主题组织的学习文档
- `examples/`：与文档章节一一对应的可运行示例

## 快速开始

```bash
uv sync
uv run python -m unittest discover -s tests -v
```

运行示例前先设置：

```bash
export OPENAI_API_KEY="[TODO: 填写你的 OpenAI API Key]"
export OPENAI_MODEL="gpt-4.1-mini"
# 如果你使用兼容 OpenAI 协议的供应商，再补 OPENAI_BASE_URL
```

运行示例时统一使用 `uv run`，例如：

```bash
uv run python examples/01_models/model_basics.py
```

优先学习顺序见 [docs/langchain-langgraph/README.md](./docs/langchain-langgraph/README.md)。
