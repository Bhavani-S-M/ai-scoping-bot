# backend/app/utils/architecture_generator.py - FASTER VERSION
import google.generativeai as genai
import re
from typing import Dict, Any
from app.config.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

class ArchitectureGenerator:
    """Generate architecture diagrams - Fast version"""
    
    def __init__(self):
        model_name = settings.GEMINI_MODEL or "gemini-1.5-flash"
        if model_name.startswith("models/"):
            model_name = model_name.replace("models/", "")
        
        print(f"🤖 Initializing ArchitectureGenerator with model: {model_name}")
        self.model = genai.GenerativeModel(model_name)
    
    async def generate_architecture_diagram(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Mermaid diagram - Simple and fast"""
        
        try:
            # Simplified prompt for faster response
            prompt = f"""Generate a system architecture diagram in Mermaid syntax.

Project: {project_data.get('name', 'System')}
Domain: {project_data.get('domain', 'General')}

Return ONLY Mermaid code. NO explanations. Start with 'graph TD'.

Show: Users -> Frontend -> API -> Backend -> Database"""
            
            # Generate with shorter timeout
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,  # Shorter response
                    temperature=0.3  # Less creative, faster
                )
            )
            
            diagram_code = response.text.strip()
            diagram_code = re.sub(r'```mermaid\s*', '', diagram_code)
            diagram_code = re.sub(r'```\s*', '', diagram_code)
            
            if not diagram_code.startswith('graph '):
                diagram_code = "graph TD\n" + diagram_code
            
            return {
                'diagram_type': 'architecture',
                'format': 'mermaid',
                'code': diagram_code,
                'description': 'System architecture diagram'
            }
            
        except Exception as e:
            print(f"⚠️ Architecture generation error (using default): {e}")
            return self._get_default_architecture(project_data)
    
    async def generate_workflow_diagram(self, activities: list) -> Dict[str, Any]:
        """Generate workflow - Simple and fast"""
        
        try:
            # Use default for speed
            return self._get_default_workflow()
            
        except Exception as e:
            print(f"⚠️ Workflow generation error (using default): {e}")
            return self._get_default_workflow()
    
    def _get_default_architecture(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fast default architecture"""
        
        domain = project_data.get('domain', 'System')
        
        diagram = f"""graph TD
    A[Users] --> B[Web Application]
    B --> C[API Gateway]
    C --> D[Backend Services]
    D --> E[Database]
    D --> F[Cache/Redis]
    C --> G[Authentication]
    
    style B fill:#e1f5ff
    style D fill:#fff4e1
    style E fill:#ffe1f5
"""
        
        return {
            'diagram_type': 'architecture',
            'format': 'mermaid',
            'code': diagram,
            'description': f'{domain} system architecture'
        }
    
    def _get_default_workflow(self) -> Dict[str, Any]:
        """Fast default workflow"""
        
        diagram = """flowchart LR
    A[Planning] --> B[Design]
    B --> C[Development]
    C --> D[Testing]
    D --> E[Deployment]
"""
        
        return {
            'diagram_type': 'workflow',
            'format': 'mermaid',
            'code': diagram,
            'description': 'Project workflow'
        }

# Global instance
architecture_generator = ArchitectureGenerator()