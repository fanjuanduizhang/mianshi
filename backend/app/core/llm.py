import json
import httpx
from app.config import settings


async def call_llm(prompt: str, max_tokens: int = 2000) -> str:
    if not settings.DEEPSEEK_API_KEY:
        return "请配置DEEPSEEK_API_KEY以使用AI功能"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
    }

    messages = [
        {
            "role": "system",
            "content": "你是一位专业的AI求职面试助手，精通技术面试和简历优化。请用简洁、专业的语言回答问题。",
        },
        {"role": "user", "content": prompt},
    ]

    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                settings.DEEPSEEK_API_URL, headers=headers, json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"调用AI服务失败: {str(e)}"


def parse_json_response(response: str, default=None):
    try:
        start_idx = response.find("{")
        end_idx = response.rfind("}") + 1
        json_str = response[start_idx:end_idx]
        return json.loads(json_str)
    except:
        return default if default is not None else {}
