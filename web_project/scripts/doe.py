import os


def main():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("请先通过环境变量 DEEPSEEK_API_KEY 提供 API 密钥。")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit("该可选脚本需要先安装 openai Python 包。") from exc

    client = OpenAI(
        api_key=api_key,
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    )
    response = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "如何学习 Python"},
        ],
        stream=True,
    )

    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
    print()


if __name__ == "__main__":
    main()
