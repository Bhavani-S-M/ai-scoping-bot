#backend/app/config/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Auth
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    # AI Services
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL")  # or "gemini-1.0-pro"
    
    JINA_API_KEY = os.getenv("JINA_API_KEY")
    JINA_MODEL = os.getenv("JINA_MODEL")  # or "jina-embeddings-v2-base-code"
    # Frontend
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # ChromaDB
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

settings = Settings()