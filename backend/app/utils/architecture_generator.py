# backend/app/utils/architecture_generator.py
import google.generativeai as genai
import json
import re
from typing import Dict, Any
from app.config.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

class ArchitectureGenerator:
    """Generate architecture diagrams in Mermaid format"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def generate_architecture_diagram(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Mermaid diagram based on project data"""
        
        prompt = f"""
Generate a system architecture diagram in Mermaid syntax for this project:

Project: {project_data.get('name')}
Domain: {project_data.get('domain')}
Tech Stack: {project_data.get('tech_stack')}

CRITICAL: Return ONLY valid Mermaid diagram syntax. NO markdown backticks, NO explanations.

Create a comprehensive architecture showing:
1. User/Client Layer
2. Frontend Components
3. Backend/API Layer
4. Database Layer
5. External Services/Integrations
6. Security Components (if applicable)

Use Mermaid graph TD or flowchart syntax.
Use clear labels and connections.

Example format:
graph TD
    A[User/Client] --> B[Frontend]
    B --> C[API Gateway]
    C --> D[Backend Services]
    D --> E[Database]
    D --> F[External APIs]
"""
        
        try:
            response = self.model.generate_content(prompt)
            diagram_code = response.text.strip()
            
            # Clean the response
            diagram_code = re.sub(r'```mermaid\s*', '', diagram_code)
            diagram_code = re.sub(r'```\s*', '', diagram_code)
            
            # Validate it starts with graph or flowchart
            if not (diagram_code.startswith('graph ') or diagram_code.startswith('flowchart ')):
                diagram_code = "graph TD\n" + diagram_code
            
            return {
                'diagram_type': 'architecture',
                'format': 'mermaid',
                'code': diagram_code,
                'description': 'System architecture diagram'
            }
            
        except Exception as e:
            print(f"Architecture generation error: {e}")
            return self._get_default_architecture(project_data)
    
    async def generate_workflow_diagram(self, activities: list) -> Dict[str, Any]:
        """Generate workflow diagram from activities"""
        
        activity_text = "\n".join([
            f"- {act.get('name')} ({act.get('phase')})"
            for act in activities[:15]  # Limit to prevent huge diagrams
        ])
        
        prompt = f"""
Generate a workflow/process diagram in Mermaid syntax for these project activities:

{activity_text}

CRITICAL: Return ONLY valid Mermaid flowchart syntax. NO markdown, NO explanations.

Show the flow of activities through project phases.
Use flowchart LR (left to right) format.
Group activities by phase.

Example:
flowchart LR
    A[Requirements] --> B[Design]
    B --> C[Development]
    C --> D[Testing]
    D --> E[Deployment]
"""
        
        try:
            response = self.model.generate_content(prompt)
            diagram_code = response.text.strip()
            
            # Clean response
            diagram_code = re.sub(r'```mermaid\s*', '', diagram_code)
            diagram_code = re.sub(r'```\s*', '', diagram_code)
            
            if not diagram_code.startswith('flowchart '):
                diagram_code = "flowchart LR\n" + diagram_code
            
            return {
                'diagram_type': 'workflow',
                'format': 'mermaid',
                'code': diagram_code,
                'description': 'Project workflow diagram'
            }
            
        except Exception as e:
            print(f"Workflow generation error: {e}")
            return self._get_default_workflow()
    
    def _get_default_architecture(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic default architecture"""
        
        diagram = f"""graph TD
    A[Users/Clients] --> B[Frontend Layer]
    B --> C[API Gateway]
    C --> D[Backend Services]
    D --> E[Database]
    D --> F[External Services]
    C --> G[Authentication]
    
    style B fill:#e1f5ff
    style D fill:#fff4e1
    style E fill:#ffe1f5
"""
        
        return {
            'diagram_type': 'architecture',
            'format': 'mermaid',
            'code': diagram,
            'description': 'Basic system architecture'
        }
    
    def _get_default_workflow(self) -> Dict[str, Any]:
        """Generate basic default workflow"""
        
        diagram = """flowchart LR
    A[Planning] --> B[Design]
    B --> C[Development]
    C --> D[Testing]
    D --> E[Deployment]
    E --> F[Maintenance]
"""
        
        return {
            'diagram_type': 'workflow',
            'format': 'mermaid',
            'code': diagram,
            'description': 'Project workflow'
        }

# Global instance
architecture_generator = ArchitectureGenerator()