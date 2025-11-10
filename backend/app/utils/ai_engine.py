# backend/app/utils/ai_engine.py
import google.generativeai as genai
import requests
import json
import os
from typing import Dict, Any, List, Optional
from app.config.config import settings
import re

# Configure Gemini
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
except Exception as e:
    print(f"Gemini configuration failed: {e}")

async def get_jina_embeddings(text: str) -> List[float]:
    """Get embeddings from Jina AI"""
    try:
        if not settings.JINA_API_KEY or settings.JINA_API_KEY == "demo-key":
            return []  # Return empty if no API key
            
        headers = {
            'Authorization': f'Bearer {settings.JINA_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'input': [text],
            'model': settings.JINA_MODEL,
            'task': 'text-matching'
        }
        
        response = requests.post(
            'https://api.jina.ai/v1/embeddings',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            embeddings = response.json()['data'][0]['embedding']
            return embeddings
        else:
            print(f"Jina API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Jina embeddings error: {e}")
        return []

# Keep other existing functions for backward compatibility
async def generate_project_scope(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Legacy function - redirects to new comprehensive function"""
    return await generate_comprehensive_scope(project_data)

async def generate_questions(project_context: str) -> List[Dict[str, str]]:
    """Legacy function - redirects to new function"""
    result = await analyze_project_and_generate_questions({'use_cases': project_context})
    return result.get('questions', [])

# Add any other existing functions that were in your original ai_engine.py