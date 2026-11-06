from __future__ import annotations

from learning_langchain.models import build_chat_model
from learning_langchain.utils.env import missing_env_message


def main() -> None:
    try:
        model = build_chat_model()
    except ValueError:
        print(missing_env_message())
        return

    response = model.invoke("用一句话解释 LangChain 和 LangGraph 的分工。")
    print(response.content)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
