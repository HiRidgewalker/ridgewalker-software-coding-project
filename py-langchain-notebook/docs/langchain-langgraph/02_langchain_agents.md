# 02. LangChain Agent 主线

前置阅读：`01_environment_and_models.md`

## 1. 是什么

LangChain agent 负责把模型、消息和工具调用组合成一个“模型自己决定下一步动作”的执行循环，适合先把 AI 能力快速接到业务上。

## 2. 工程中何时用

- 需要一个会自动选工具的业务助手
- 业务步骤不复杂，先验证 MVP
- 希望先用高层抽象跑通，再决定是否下沉到 LangGraph

## 3. 核心 API / 用法（带注释的完整示例）

```python
from langchain.agents import create_agent
from langchain.tools import tool

from learning_langchain.models import build_chat_model


@tool
def get_exchange_rate(base: str, target: str) -> str:
    """返回固定汇率，保证本地学习示例稳定。"""
    rates = {("USD", "CNY"): 7.18}
    return f"1 {base} = {rates[(base, target)]} {target}"


agent = create_agent(
    model=build_chat_model(),
    tools=[get_exchange_rate],
    # system_prompt 直接定义工具使用边界，避免模型胡乱发挥
    system_prompt="你是金融助手，遇到确定性数据时优先调用工具。",
)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "把 100 美元换算成人民币，并说明你有没有调用工具。",
            }
        ]
    }
)

print(result["messages"][-1].content)
```

补充说明：

- `@tool` 会把普通 Python 函数注册成 LangChain agent 可调用的工具。
- 函数名会成为工具名；这里的工具名就是 `get_exchange_rate`。
- 参数签名 `base: str, target: str` 会被转换成工具参数 schema，模型会按这个结构生成调用参数。
- docstring 会成为工具描述，直接影响模型是否知道“这个工具适合查汇率”。
- 没有 `@tool` 时，这个函数只是普通函数，Python 代码可以手动调用，但 agent 不会把它当成标准工具来理解和选择。

## 4. 工程最佳实践

✅ 推荐：把 agent 当成业务入口，不要把所有流程判断都塞进 prompt。  
✅ 推荐：先少量高质量工具，再逐步扩工具集。  
✅ 推荐：工具返回尽量稳定、结构清晰、可复现。  
❌ 避免：一开始就塞十几个工具，导致模型频繁误选。  
❌ 避免：把复杂审批和恢复需求继续硬扛在 LangChain agent 上。  

## 5. 与其他特性的关联

- 工具定义详见 `03_tools_and_structured_output.md`
- 线程级上下文见 `04_short_term_memory_and_context.md`
- 一旦进入复杂流程，应迁移到 `05` 到 `07`
