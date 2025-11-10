#backend/app/utils/enhanced_ai_engine.py
import google.generativeai as genai
import requests
import json
import os
import re
from typing import Dict, Any, List, Optional
from app.config.config import settings
from .rag_engine import rag_engine

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

class EnhancedAIEngine:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def analyze_project_with_rag(self, project_data: Dict[str, Any], uploaded_content: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced project analysis with RAG"""
        try:
            # Build search query
            search_query = self._build_search_query(project_data, uploaded_content)
            
            # Search similar projects with domain filter
            filters = {"domain": project_data.get('domain')} if project_data.get('domain') else None
            similar_projects = await rag_engine.search_similar_projects(
                query=search_query, 
                filters=filters,
                n_results=3
            )
            
            # Generate questions with RAG context
            rag_context = self._build_rag_context(similar_projects)
            questions_result = await self._generate_questions_with_context(project_data, uploaded_content, rag_context)
            
            return {
                **questions_result,
                "similar_projects": similar_projects.get("similar_projects", []),
                "rag_used": len(similar_projects.get("similar_projects", [])) > 0
            }
            
        except Exception as e:
            print(f"RAG analysis error: {e}")
            return await self._fallback_analysis(project_data)
    
    async def generate_scope_with_rag(self, 
                                    project_data: Dict[str, Any], 
                                    answered_questions: List[Dict[str, Any]],
                                    similar_projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate scope using RAG-enhanced context"""
        try:
            # Build comprehensive context
            context = self._build_scope_context(project_data, answered_questions, similar_projects)
            
            prompt = f"""
You are an expert project manager. Generate a COMPREHENSIVE project scope using both the project details and insights from similar historical projects.

{context}

Generate a detailed JSON response with ALL these sections:

{{
  "overview": {{
    "project_summary": "Detailed 3-4 sentence summary",
    "key_objectives": ["objective1", "objective2"],
    "success_metrics": ["metric1", "metric2"],
    "deliverables": ["deliverable1", "deliverable2"]
  }},
  "timeline": {{
    "total_duration_months": 6,
    "phases": [
      {{
        "phase_name": "Planning",
        "duration_weeks": 4,
        "milestones": ["milestone1"],
        "activities": ["activity1"]
      }}
    ]
  }},
  "activities": [
    {{
      "name": "Activity Name",
      "phase": "Planning",
      "effort_days": 10,
      "dependencies": [],
      "resources_needed": ["Role1"]
    }}
  ],
  "resources": [
    {{
      "role": "Role Name",
      "count": 1,
      "effort_months": 6,
      "monthly_rate": 8000,
      "total_cost": 48000
    }}
  ],
  "architecture": {{
    "description": "Architecture overview",
    "components": [
      {{
        "name": "Component",
        "technology": "Tech",
        "description": "Description"
      }}
    ]
  }},
  "cost_breakdown": {{
    "total_cost": 250000,
    "contingency_percentage": 15,
    "contingency_amount": 37500
  }},
  "risks": [
    {{
      "risk": "Risk description",
      "severity": "High",
      "mitigation": "Mitigation plan"
    }}
  ]
}}

Use insights from similar projects to make realistic estimates. Include 15-20 activities.
"""
            
            response = self.model.generate_content(prompt)
            scope = self._parse_json_response(response.text)
            
            # Enhance with RAG insights
            scope = self._enhance_scope_with_rag_insights(scope, similar_projects)
            
            return scope
            
        except Exception as e:
            print(f"RAG scope generation error: {e}")
            return self._get_fallback_scope(project_data)
    
    def _build_search_query(self, project_data: Dict[str, Any], uploaded_content: Optional[str] = None) -> str:
        """Build search query for RAG"""
        query_parts = [
            project_data.get('name', ''),
            project_data.get('domain', ''),
            project_data.get('complexity', ''),
            project_data.get('tech_stack', ''),
            project_data.get('use_cases', '')
        ]
        
        if uploaded_content:
            query_parts.append(uploaded_content[:500])  # Limit content length
        
        return " ".join(filter(None, query_parts))
    
    def _build_rag_context(self, similar_projects: Dict[str, Any]) -> str:
        """Build context from similar projects"""
        if not similar_projects.get("similar_projects"):
            return "No similar historical projects found."
        
        context = "INSIGHTS FROM SIMILAR HISTORICAL PROJECTS:\n\n"
        
        for i, project in enumerate(similar_projects["similar_projects"][:3], 1):
            context += f"Project {i}: {project['project_name']}\n"
            context += f"Domain: {project['domain']} | Complexity: {project['complexity']}\n"
            context += f"Cost: ${project['total_cost']:,} | Duration: {project['duration']} months\n"
            context += f"Similarity: {project['similarity_score']:.2f}\n"
            
            if project.get('key_insights'):
                context += "Key Insights:\n"
                for insight in project['key_insights']:
                    context += f"  • {insight}\n"
            
            context += "\n"
        
        return context
    
    def _build_scope_context(self, 
                           project_data: Dict[str, Any], 
                           answered_questions: List[Dict[str, Any]],
                           similar_projects: List[Dict[str, Any]]) -> str:
        """Build comprehensive context for scope generation"""
        context = f"""
PROJECT DETAILS:
- Name: {project_data.get('name')}
- Domain: {project_data.get('domain')}
- Complexity: {project_data.get('complexity')}
- Tech Stack: {project_data.get('tech_stack')}
- Use Cases: {project_data.get('use_cases')}
"""
        
        # Add answered questions
        if answered_questions:
            context += "\nCLARIFYING ANSWERS:\n"
            for q in answered_questions:
                context += f"Q: {q.get('question')}\nA: {q.get('answer')}\n\n"
        
        # Add RAG insights
        if similar_projects:
            context += "\nHISTORICAL PROJECT INSIGHTS:\n"
            for project in similar_projects[:2]:
                context += f"• Similar project '{project['project_name']}': {project['duration']} months, ${project['total_cost']:,}\n"
                for insight in project.get('key_insights', [])[:2]:
                    context += f"  - {insight}\n"
        
        return context
    
    async def _generate_questions_with_context(self, 
                                            project_data: Dict[str, Any], 
                                            uploaded_content: Optional[str],
                                            rag_context: str) -> Dict[str, Any]:
        """Generate questions with RAG context"""
        prompt = f"""
You are an expert project consultant. Generate clarifying questions using both the project info and insights from similar historical projects.

PROJECT INFO:
- Name: {project_data.get('name')}
- Domain: {project_data.get('domain')}
- Complexity: {project_data.get('complexity')}
- Tech Stack: {project_data.get('tech_stack')}
- Use Cases: {project_data.get('use_cases')}

{rag_context}

{UPLOADED_DOCUMENTS if uploaded_content else ''}

Generate 5-8 smart questions across these categories:
1. Technical Requirements
2. Business Requirements  
3. Timeline & Resources
4. Compliance & Security

Return ONLY valid JSON array with this structure:
[
  {{
    "id": "q1",
    "category": "Technical Requirements",
    "question": "Specific question?",
    "importance": "high|medium|low",
    "suggested_answers": ["Option A", "Option B"]
  }}
]
"""
        
        response = self.model.generate_content(prompt)
        questions = self._parse_json_response(response.text)
        
        return {
            "questions": questions,
            "initial_analysis": await self._generate_initial_analysis(project_data, rag_context)
        }
    
    async def _generate_initial_analysis(self, project_data: Dict[str, Any], rag_context: str) -> Dict[str, Any]:
        """Generate initial project analysis"""
        prompt = f"""
Based on this project and similar historical data, provide initial analysis:

PROJECT: {project_data.get('name')} - {project_data.get('domain')}
COMPLEXITY: {project_data.get('complexity')}

{rag_context}

Return ONLY valid JSON:
{{
  "summary": "2-3 sentence summary",
  "key_challenges": ["challenge1", "challenge2"],
  "recommended_approach": "Brief approach description",
  "estimated_complexity": "simple|medium|complex",
  "missing_information": ["info1", "info2"]
}}
"""
        
        response = self.model.generate_content(prompt)
        return self._parse_json_response(response.text)
    
    def _enhance_scope_with_rag_insights(self, scope: Dict[str, Any], similar_projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance scope with insights from similar projects"""
        if not similar_projects:
            return scope
        
        # Use insights from most similar project
        most_similar = similar_projects[0]
        
        # Adjust timeline if similar project suggests different duration
        similar_duration = most_similar.get('duration', 0)
        current_duration = scope.get('timeline', {}).get('total_duration_months', 0)
        
        if similar_duration > 0 and abs(current_duration - similar_duration) / similar_duration > 0.3:
            # Adjust if difference is more than 30%
            scope['timeline']['total_duration_months'] = similar_duration
            scope['timeline']['adjustment_note'] = f"Adjusted based on similar {most_similar['domain']} project"
        
        # Add RAG insights section
        scope['rag_insights'] = {
            "similar_projects_count": len(similar_projects),
            "most_similar_project": most_similar['project_name'],
            "similarity_score": most_similar['similarity_score'],
            "historical_reference": True
        }
        
        return scope
    
    def _parse_json_response(self, response_text: str) -> Any:
        """Parse JSON from AI response"""
        try:
            # Clean response text
            text = re.sub(r'```json\s*', '', response_text)
            text = re.sub(r'```\s*', '', text).strip()
            
            # Find JSON object or array
            start = max(text.find('{'), text.find('['))
            if start == -1:
                raise ValueError("No JSON found")
            
            end = max(text.rfind('}'), text.rfind(']')) + 1
            json_str = text[start:end]
            
            return json.loads(json_str)
        except Exception as e:
            print(f"JSON parsing error: {e}")
            raise
    
    async def _fallback_analysis(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when RAG fails"""
        return {
            "questions": [
                {
                    "id": "q1",
                    "category": "Technical Requirements",
                    "question": "What are your specific technical requirements?",
                    "importance": "high",
                    "suggested_answers": []
                }
            ],
            "initial_analysis": {
                "summary": "Initial analysis pending",
                "key_challenges": [],
                "recommended_approach": "Standard approach",
                "estimated_complexity": project_data.get('complexity', 'medium'),
                "missing_information": []
            },
            "similar_projects": [],
            "rag_used": False
        }
    
    def _get_fallback_scope(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback scope generation"""
        return {
            "overview": {
                "project_summary": f"Project scoping for {project_data.get('name', 'Unknown')}",
                "key_objectives": ["Deliver quality solution"],
                "success_metrics": ["Client satisfaction"],
                "deliverables": ["Final deliverable"]
            },
            "timeline": {"total_duration_months": 3, "phases": []},
            "activities": [],
            "resources": [],
            "architecture": {},
            "cost_breakdown": {"total_cost": 0},
            "risks": []
        }

# Global instance
enhanced_ai_engine = EnhancedAIEngine()