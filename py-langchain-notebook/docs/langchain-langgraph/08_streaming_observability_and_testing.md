# 08. 流式输出、可观测性与测试

前置阅读：`02_langchain_agents.md`、`05_langgraph_state_and_nodes.md`

## 1. 是什么

流式输出解决用户等待体验，可观测性解决你为什么跑成这样，测试解决你改完以后还敢不敢上线；三者一起决定 agent 项目能不能长期维护。

## 2. 工程中何时用

- 需要边生成边返回结果给前端
- 需要定位为什么路由错了、工具选错了、状态没更新
- 需要给学习示例和真实业务都建立最小回归保护

## 3. 核心 API / 用法（带注释的完整示例）

```python
from langchain.agents import create_agent
from langchain.tools import tool

from learning_langchain.models import build_chat_model


@tool
def get_service_status(service_name: str) -> str:
    """返回一个固定状态，方便学习流式工具调用。"""
    return f"{service_name} is healthy"


agent = create_agent(model=build_chat_model(), tools=[get_service_status])

for token, metadata in agent.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "先检查 billing-service 状态，再说明为什么生产 agent 需要可观测性。",
            }
        ]
    },
    # stream_mode=\"messages\" 会同时吐出模型 token 和工具调用片段
    stream_mode="messages",
):
    if token.content_blocks:
        print(metadata["langgraph_node"], token.content_blocks)
```

## 4. 工程最佳实践

✅ 推荐：至少给配置层和关键示例入口加 smoke test。  
✅ 推荐：把路由结果、线程 ID、人工审批节点明确打印或记录。  
✅ 推荐：先让关键路径可观测，再谈复杂优化。  
❌ 避免：问题出现后只能看最终答案，看不到中间状态。  
❌ 避免：所有示例都靠手工运行验证，没有自动校验。  

## 5. 与其他特性的关联

- 流式输出常和 `02_langchain_agents.md` 中的交互式 CLI 联用
- 调试和测试会覆盖 `03` 到 `07` 的所有核心能力
