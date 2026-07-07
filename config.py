import os
from dotenv import load_dotenv

load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")

CHROMADB_PATH = os.path.join(os.path.dirname(__file__), "data", "chromadb")
RESUME_UPLOAD_PATH = os.path.join(os.path.dirname(__file__), "data", "uploads")
QUESTION_BANK_PATH = os.path.join(os.path.dirname(__file__), "data", "question_bank")

os.makedirs(CHROMADB_PATH, exist_ok=True)
os.makedirs(RESUME_UPLOAD_PATH, exist_ok=True)
os.makedirs(QUESTION_BANK_PATH, exist_ok=True)