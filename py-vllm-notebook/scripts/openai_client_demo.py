from openai import OpenAI


LOCAL_MODEL_ID = "models/Qwen/Qwen3.5-2B"


def main() -> None:
    client = OpenAI(
        base_url="http://localhost:8000/v1",
        api_key="EMPTY",
    )

    models = client.models.list()
    print("=== Available Models ===")
    for model in models.data:
        print(model.id)
    print()

    response = client.chat.completions.create(
        model=LOCAL_MODEL_ID,
        messages=[
            {
                "role": "system",
                "content": "You are a concise assistant focused on vLLM deployment.",
            },
            {
                "role": "user",
                "content": "请用三点说明 vLLM 本地部署时最重要的调参项。",
            },
        ],
        temperature=0.7,
        max_tokens=256,
    )

    print("=== Chat Response ===")
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
