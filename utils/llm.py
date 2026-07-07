import requests
import json
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL

def call_llm(prompt: str, max_tokens: int = 2000) -> str:
    if not DEEPSEEK_API_KEY:
        return "请在.env文件中配置DEEPSEEK_API_KEY以使用AI功能"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    messages = [
        {
            "role": "system",
            "content": "你是一位专业的AI求职面试助手，精通技术面试和简历优化。请用简洁、专业的语言回答问题。"
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"调用AI服务失败: {str(e)}"