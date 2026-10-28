import requests

test = '手语'
url = 'http://localhost:11434/api/embeddings'  # 修正拼写

try:
    res = requests.post(
        url=url,
        json={
            "model": "qwen2.5:1.5b",
            "prompt": test  # 使用变量test作为prompt
        }
    )
    res.raise_for_status()  # 检查HTTP错误
    embeddings = res.json().get('embedding')
    print(test)
    print(len(embeddings), embeddings)
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
except ValueError as e:
    print(f"JSON decode error: {e}")
    print(f"Response content: {res.text}")