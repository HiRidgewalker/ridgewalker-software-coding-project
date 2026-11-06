from __future__ import annotations

from pydantic import BaseModel, Field

from learning_langchain.models import build_chat_model
from learning_langchain.utils.env import missing_env_message


class TicketIntent(BaseModel):
    category: str = Field(description="Ticket category such as billing or support.")
    urgency: str = Field(description="One of low, medium, high.")
    needs_human: bool = Field(description="Whether this should be escalated.")


def main() -> None:
    try:
        model = build_chat_model()
    except ValueError:
        print(missing_env_message())
        return

    structured_model = model.with_structured_output(TicketIntent)
    result = structured_model.invoke("客户说付款成功但账号还没开通，比较着急。")
    print(result.model_dump())


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
