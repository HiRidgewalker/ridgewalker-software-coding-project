# 01. 环境与模型接入

## 1. 是什么

这一部分解决“把最新 LangChain / LangGraph 示例真正跑起来”的基础问题，包括 Python 环境、依赖、API Key 和 OpenAI-compatible base URL。

## 2. 工程中何时用

- 新项目初始化，需要统一依赖和环境变量命名
- 团队同时接 OpenAI 官方接口和兼容 OpenAI 协议的供应商
- 需要给示例、测试、脚本提供一致的模型构建入口

## 3. 核心 API / 用法（带注释的完整示例）

```python
import os

from langchain_openai import ChatOpenAI


def build_model() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
        api_key=os.environ["OPENAI_API_KEY"],
        # 兼容 OpenAI 协议的供应商可以在这里指定，例如 [TODO: 填写你的供应商 base URL]
        base_url=os.environ.get("OPENAI_BASE_URL") or None,
        temperature=0,
    )


if __name__ == "__main__":
    model = build_model()
    result = model.invoke("用一句话说明 LangChain 和 LangGraph 的区别。")
    print(result.content)
```

## 4. 工程最佳实践

✅ 推荐：统一使用 `OPENAI_API_KEY`、`OPENAI_MODEL`、`OPENAI_BASE_URL` 三个环境变量。  
✅ 推荐：封装单一的 `build_model()` 入口，避免示例各自拼参数。  
✅ 推荐：默认模型选小型高质量模型，学习阶段先追求快反馈。  
❌ 避免：在示例里硬编码 API Key。  
❌ 避免：每个脚本都写一套不同的模型初始化代码。  

## 5. 与其他特性的关联

- `02_langchain_agents.md` 会直接复用这里的模型构建入口
- `03` 到 `08` 的所有示例都依赖这层统一配置
