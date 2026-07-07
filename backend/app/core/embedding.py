import httpx
import numpy as np
from app.config import settings


async def generate_embedding(text: str) -> list:
    if not settings.DASHSCOPE_API_KEY:
        return _fallback_embedding(text)

    url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding-v3/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
    }
    data = {
        "input": text,
        "model": "text-embedding-v3",
        "parameters": {"embedding_type": "float", "dimensions": 1024},
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["output"]["embeddings"][0]["embedding"]
    except Exception:
        return _fallback_embedding(text)


def _fallback_embedding(text: str) -> list:
    words = text.lower().split()
    vocab = {}
    idx = 0
    vec = [0.0] * 384
    for w in words:
        if w not in vocab:
            vocab[w] = idx
            idx += 1
        h = hash(w) % 384
        vec[h] += 1.0
    norm = np.linalg.norm(vec) if np.linalg.norm(vec) > 0 else 1.0
    return (np.array(vec) / norm).tolist()
