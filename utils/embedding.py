import requests
import numpy as np
from config import DASHSCOPE_API_KEY

def generate_embedding(text: str) -> list:
    if not DASHSCOPE_API_KEY:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model.encode(text).tolist()
    
    url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding-v3/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}"
    }
    data = {
        "input": text,
        "model": "text-embedding-v3",
        "parameters": {
            "embedding_type": "float",
            "dimensions": 1024
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result["output"]["embeddings"][0]["embedding"]
    except Exception as e:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model.encode(text).tolist()