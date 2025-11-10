# backend/app/utils/ai_engine.py
import google.generativeai as genai
import requests
import json
from typing import List
from app.config.config import settings

# Configure Gemini
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    print("✅ Gemini API configured successfully")
except Exception as e:
    print(f"❌ Gemini configuration failed: {e}")

async def get_jina_embeddings(text: str) -> List[float]:
    """Get embeddings from Jina AI - OPTIONAL, returns empty list if fails"""
    try:
        # Check if Jina is configured
        if not settings.JINA_API_KEY or settings.JINA_API_KEY == "demo-key":
            print("⚠️ Jina API key not configured, skipping embeddings")
            return []
        
        headers = {
            'Authorization': f'Bearer {settings.JINA_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Limit text length to avoid 422 errors
        text = text[:5000]  # Jina has token limits
        
        data = {
            'input': [text],
            'model': settings.JINA_MODEL or 'jina-embeddings-v2-base-en'
        }
        
        response = requests.post(
            'https://api.jina.ai/v1/embeddings',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            embeddings = response.json()['data'][0]['embedding']
            print(f"✅ Jina embeddings generated ({len(embeddings)} dimensions)")
            return embeddings
        else:
            print(f"⚠️ Jina API error {response.status_code}: {response.text[:200]}")
            return []
            
    except Exception as e:
        print(f"⚠️ Jina embeddings error (non-critical): {e}")
        return []