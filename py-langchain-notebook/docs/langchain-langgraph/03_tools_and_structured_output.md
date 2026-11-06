# 03. 工具与结构化输出

前置阅读：`01_environment_and_models.md`、`02_langchain_agents.md`

## 1. 是什么

工具让模型安全地调用外部能力，结构化输出让模型结果变成稳定的数据结构；这两件事是生产代码里最常见的 LLM 控制手段。

## 2. 工程中何时用

- 需要查库存、汇率、工单、订单等确定性数据
- 需要把模型输出落成 JSON / Pydantic 对象供后续代码使用
- 需要限制模型只能输出符合业务约束的字段

## 3. 核心 API / 用法（带注释的完整示例）

```python
from pydantic import BaseModel, Field

from learning_langchain.models import build_chat_model


class TicketIntent(BaseModel):
    category: str = Field(description="工单分类，例如 billing、support")
    urgency: str = Field(description="优先级：low、medium、high")
    needs_human: bool = Field(description="是否需要人工接手")


model = build_chat_model()
structured_model = model.with_structured_output(TicketIntent)

result = structured_model.invoke("客户说付款成功但账号还没开通，比较着急。")
print(result.model_dump())
```

## 4. 工程最佳实践

✅ 推荐：工具负责“查和做”，模型负责“判断和解释”。  
✅ 推荐：结构化输出优先用显式 schema，不要靠字符串约定。  
✅ 推荐：字段命名贴近业务语义，方便后续代码直接消费。  
❌ 避免：让模型自由输出一大段 JSON 文本再自己正则提取。  
❌ 避免：把副作用很强的动作伪装成无害工具。  

## 5. 与其他特性的关联

- 工具常和 `02_langchain_agents.md` 联用
- 结构化输出经常作为 `05`、`06` 里图节点的输入或路由依据
