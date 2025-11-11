# backend/app/utils/document_parser.py
import PyPDF2
import docx
import json
import re
from typing import Dict, Any, Optional
import google.generativeai as genai
from app.config.config import settings

# CRITICAL FIX: Configure Gemini with correct model name
genai.configure(api_key=settings.GEMINI_API_KEY)

class DocumentParser:
    """Enhanced document parser with entity extraction"""
    
    def __init__(self):
        # FIX: Use simple model name without "models/" prefix
        model_name = settings.GEMINI_MODEL or "gemini-1.5-flash"
        
        # Ensure we don't add "models/" prefix
        if model_name.startswith("models/"):
            model_name = model_name.replace("models/", "")
        
        print(f"🤖 Initializing DocumentParser with model: {model_name}")
        self.model = genai.GenerativeModel(model_name)
    
    async def parse_document(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Parse document and extract text"""
        text = ""
        
        if file_type == 'pdf':
            text = self._extract_pdf_text(file_path)
        elif file_type in ['docx', 'doc']:
            text = self._extract_docx_text(file_path)
        elif file_type == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        return {
            'raw_text': text,
            'word_count': len(text.split()),
            'char_count': len(text)
        }
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"PDF extraction error: {e}")
        return text
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"DOCX extraction error: {e}")
        return text
    
    async def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract key project entities using AI"""
        
        prompt = f"""
You are an expert at analyzing project documents (RFPs, SOWs, requirements).
Extract the following key entities from the document below:

CRITICAL: Return ONLY a valid JSON object. NO markdown, NO backticks, NO extra text.

Extract these fields:
- project_type: (e.g., "Web Application", "Mobile App", "API Integration")
- domain: (e.g., "Healthcare", "Finance", "E-commerce")
- complexity: (MUST be one of: "simple", "moderate", "complex", "enterprise")
- deliverables: (array of main deliverables)
- tech_stack: (array of technologies mentioned)
- compliance_requirements: (array of compliance standards like GDPR, HIPAA)
- estimated_duration: (e.g., "6 months", "12 weeks")
- key_features: (array of main features/capabilities)
- integration_requirements: (array of systems to integrate with)
- security_requirements: (array of security needs)
- user_roles: (array of user types/roles)
- scalability_needs: (description of scale requirements)
- budget_indicators: (any budget/cost mentions)

IMPORTANT: For complexity, you MUST use ONLY these exact values:
- "simple" (for basic projects)
- "moderate" (for medium complexity - DO NOT USE "medium")
- "complex" (for advanced projects)
- "enterprise" (for large-scale enterprise projects)

Document (first 5000 chars):
{text[:5000]}

Return this exact structure:
{{
  "project_type": "string",
  "domain": "string",
  "complexity": "simple|moderate|complex|enterprise",
  "deliverables": ["item1", "item2"],
  "tech_stack": ["tech1", "tech2"],
  "compliance_requirements": ["requirement1"],
  "estimated_duration": "string",
  "key_features": ["feature1", "feature2"],
  "integration_requirements": ["system1"],
  "security_requirements": ["requirement1"],
  "user_roles": ["role1", "role2"],
  "scalability_needs": "description",
  "budget_indicators": "any cost mentions"
}}
"""
        
        try:
            print("📤 Sending entity extraction request to Gemini...")
            response = self.model.generate_content(prompt)
            text_response = response.text.strip()
            
            print(f"📥 Received response from Gemini")
            
            # Clean response
            text_response = re.sub(r'```json\s*', '', text_response)
            text_response = re.sub(r'```\s*', '', text_response)
            
            # Find JSON object
            start = text_response.find('{')
            end = text_response.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = text_response[start:end]
                entities = json.loads(json_str)
                
                # CRITICAL FIX: Ensure complexity is one of the valid values
                complexity = entities.get('complexity', 'moderate').lower()
                
                # Map any "medium" to "moderate"
                if complexity == 'medium':
                    complexity = 'moderate'
                    print(f"⚠️ Mapped 'medium' to 'moderate'")
                
                # Validate complexity
                valid_complexities = ['simple', 'moderate', 'complex', 'enterprise']
                if complexity not in valid_complexities:
                    print(f"⚠️ Invalid complexity '{complexity}', defaulting to 'moderate'")
                    complexity = 'moderate'
                
                entities['complexity'] = complexity
                
                print(f"✅ Entity extraction successful - Complexity: {complexity}")
                return entities
            else:
                raise ValueError("No JSON object found in response")
                
        except Exception as e:
            print(f"❌ Entity extraction error: {e}")
            return self._get_default_entities()
    
    def _get_default_entities(self) -> Dict[str, Any]:
        """Return default entity structure"""
        return {
            "project_type": "Not specified",
            "domain": "General",
            "complexity": "moderate",  # CHANGED: Use "moderate" instead of "medium"
            "deliverables": [],
            "tech_stack": [],
            "compliance_requirements": [],
            "estimated_duration": "Not specified",
            "key_features": [],
            "integration_requirements": [],
            "security_requirements": [],
            "user_roles": [],
            "scalability_needs": "Not specified",
            "budget_indicators": "Not specified"
        }
    
    async def parse_and_extract(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Combined parse and entity extraction"""
        
        try:
            # Parse document
            parsed_data = await self.parse_document(file_path, file_type)
            
            # Extract entities
            entities = await self.extract_entities(parsed_data['raw_text'])
            
            return {
                'parsed_text': parsed_data,
                'entities': entities,
                'extraction_confidence': 'high' if parsed_data['word_count'] > 100 else 'low'
            }
        except Exception as e:
            print(f"❌ Parse and extract error: {e}")
            import traceback
            traceback.print_exc()
            
            # Return defaults on error
            return {
                'parsed_text': {'raw_text': '', 'word_count': 0, 'char_count': 0},
                'entities': self._get_default_entities(),
                'extraction_confidence': 'low'
            }

# Global instance
document_parser = DocumentParser()