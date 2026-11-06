from __future__ import annotations

from langchain.agents import create_agent
from langchain.tools import tool

from learning_langchain.models import build_chat_model
from learning_langchain.utils.env import missing_env_message


# @tool 会把普通 Python 函数注册成 agent 可调用的工具。
# 这样模型在推理过程中就可以决定是否调用这个函数。
@tool
def get_service_status(service_name: str) -> str:
    # 这里返回固定结果，是为了让教学示例更稳定、可预期。
    # 在真实项目里，这里通常会去查监控系统、服务注册中心或健康检查接口。
    """Return deterministic status text for a service."""
    return f"{service_name} is healthy"


def main() -> None:
    try:
        # build_chat_model() 会从环境变量中读取模型配置，
        # 并返回一个可以直接调用的聊天模型实例。
        model = build_chat_model()
    except ValueError:
        # 缺少必要环境变量时，打印提示并结束程序。
        print(missing_env_message())
        return

    # create_agent() 把“模型 + 工具”组合成一个 agent。
    # 这个 agent 会自己决定：
    # 1. 是否调用工具
    # 2. 用什么参数调用
    # 3. 工具返回后如何继续生成答案
    agent = create_agent(model=model, tools=[get_service_status])

    # stream(...) 用流式方式执行 agent。
    # 和 invoke() 一次性拿最终结果不同，stream() 会边执行边返回内容块。
    for token, metadata in agent.stream(
        {
            "messages": [
                {
                    "role": "user",
                    # 这条用户消息会促使 agent：
                    # 先检查 billing-service 状态，再继续解释“可观测性”的意义。
                    "content": "先检查 billing-service 状态，再说明为什么生产 agent 需要可观测性。",
                }
            ]
        },
        # stream_mode="messages" 表示按“消息块”流式返回。
        # 这里既可能看到普通文本，也可能看到工具调用参数片段和工具执行结果。
        stream_mode="messages",
    ):
        # token 表示当前这一个流式片段。
        # metadata 里会带这块内容来自哪个 LangGraph 节点。
        #
        # 常见节点包括：
        # - model：模型正在输出文本或生成工具调用参数
        # - tools：工具节点正在返回结果
        if token.content_blocks:
            # content_blocks 是当前 chunk 的具体内容列表。
            # 这里打印出来，主要用于学习和调试 agent 的中间执行过程，
            # 观察工具调用和模型输出是如何交替发生的。
            print(metadata["langgraph_node"], token.content_blocks)

    # 补一个换行，让终端输出更整洁。
    print()


if __name__ == "__main__":
    # 先加载 .env，确保本地运行时能读到 API Key 和模型配置。
    from dotenv import load_dotenv

    load_dotenv()

    # 作为脚本执行时，进入主流程。
    main()
