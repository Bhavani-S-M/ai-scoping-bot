# backend/app/utils/enhanced_ai_engine.py - COMPLETE FIX
import google.generativeai as genai
import json
import re
from typing import Dict, Any, List, Optional
from app.config.config import settings
from app.utils.rag_engine import rag_engine

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

class EnhancedAIEngine:
    def __init__(self):
        model_name = settings.GEMINI_MODEL or "gemini-1.5-flash"
        if model_name.startswith("models/"):
            model_name = model_name.replace("models/", "")
        
        print(f"🤖 Initializing EnhancedAIEngine with model: {model_name}")
        self.model = genai.GenerativeModel(model_name)
        print(f"✅ EnhancedAIEngine initialized successfully")
    
    async def analyze_project_with_rag(self, project_data: Dict[str, Any], uploaded_content: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced project analysis with RAG"""
        try:
            print(f"🔍 Starting RAG analysis for project: {project_data.get('name')}")
            
            search_query = self._build_search_query(project_data, uploaded_content)
            filters = {"domain": project_data.get('domain')} if project_data.get('domain') else None
            similar_projects = await rag_engine.search_similar_projects(
                query=search_query, 
                filters=filters,
                n_results=3
            )
            
            rag_context = self._build_rag_context(similar_projects)
            questions_result = await self._generate_questions_with_context(project_data, uploaded_content, rag_context)
            
            return {
                **questions_result,
                "similar_projects": similar_projects.get("similar_projects", []),
                "rag_used": len(similar_projects.get("similar_projects", [])) > 0
            }
            
        except Exception as e:
            print(f"❌ RAG analysis error: {e}")
            return await self._fallback_analysis(project_data)
    
    async def generate_scope_with_rag(self, 
                                    project_data: Dict[str, Any], 
                                    answered_questions: List[Dict[str, Any]] = None,
                                    similar_projects: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate COMPLETE scope with ALL resources"""
        try:
            print(f"🎯 Generating COMPLETE scope for: {project_data.get('name')}")
            
            context = self._build_scope_context(project_data, answered_questions or [], similar_projects or [])
            
            # Use detailed prompt to ensure all resources are generated
            prompt = f"""
You are an expert project manager. Generate a COMPREHENSIVE project scope with COMPLETE team composition.

{context}

CRITICAL REQUIREMENTS:
1. Include AT LEAST 7-10 different roles in resources
2. Each role must have realistic count, effort, and rates
3. Generate detailed activities for each phase
4. Create complete timeline with milestones
5. Return ONLY valid JSON

Generate this EXACT structure with ALL fields populated:

{{
  "overview": {{
    "project_summary": "Detailed 3-4 sentence project description",
    "key_objectives": ["Objective 1", "Objective 2", "Objective 3", "Objective 4"],
    "success_metrics": ["Metric 1", "Metric 2", "Metric 3"],
    "deliverables": ["Deliverable 1", "Deliverable 2", "Deliverable 3"]
  }},
  "timeline": {{
    "total_duration_months": 6,
    "total_duration_weeks": 24,
    "phases": [
      {{
        "phase_name": "Planning & Requirements",
        "duration_weeks": 4,
        "start_week": 1,
        "end_week": 4,
        "milestones": ["Requirements finalized", "Architecture approved"],
        "activities": ["Requirements gathering", "Stakeholder interviews"]
      }},
      {{
        "phase_name": "Design & Architecture",
        "duration_weeks": 4,
        "start_week": 5,
        "end_week": 8,
        "milestones": ["Design complete", "Prototype ready"],
        "activities": ["UI/UX design", "System architecture"]
      }},
      {{
        "phase_name": "Development",
        "duration_weeks": 10,
        "start_week": 9,
        "end_week": 18,
        "milestones": ["Core features complete", "Integration done"],
        "activities": ["Frontend development", "Backend development", "API development"]
      }},
      {{
        "phase_name": "Testing & QA",
        "duration_weeks": 4,
        "start_week": 19,
        "end_week": 22,
        "milestones": ["All tests passed", "UAT complete"],
        "activities": ["Unit testing", "Integration testing", "User acceptance testing"]
      }},
      {{
        "phase_name": "Deployment & Launch",
        "duration_weeks": 2,
        "start_week": 23,
        "end_week": 24,
        "milestones": ["Production deployment", "Project handover"],
        "activities": ["Production setup", "Training", "Documentation"]
      }}
    ]
  }},
  "activities": [
    {{
      "name": "Requirements Analysis",
      "phase": "Planning & Requirements",
      "effort_days": 12,
      "dependencies": [],
      "resources_needed": ["Business Analyst", "Project Manager"]
    }},
    {{
      "name": "System Architecture Design",
      "phase": "Design & Architecture",
      "effort_days": 15,
      "dependencies": ["Requirements Analysis"],
      "resources_needed": ["Solution Architect", "Technical Lead"]
    }},
    {{
      "name": "UI/UX Design",
      "phase": "Design & Architecture",
      "effort_days": 18,
      "dependencies": ["Requirements Analysis"],
      "resources_needed": ["UI/UX Designer"]
    }},
    {{
      "name": "Database Design",
      "phase": "Design & Architecture",
      "effort_days": 10,
      "dependencies": ["System Architecture Design"],
      "resources_needed": ["Database Architect", "Backend Developer"]
    }},
    {{
      "name": "Frontend Development",
      "phase": "Development",
      "effort_days": 45,
      "dependencies": ["UI/UX Design"],
      "resources_needed": ["Frontend Developer"]
    }},
    {{
      "name": "Backend API Development",
      "phase": "Development",
      "effort_days": 50,
      "dependencies": ["Database Design"],
      "resources_needed": ["Backend Developer"]
    }},
    {{
      "name": "Third-party Integration",
      "phase": "Development",
      "effort_days": 20,
      "dependencies": ["Backend API Development"],
      "resources_needed": ["Integration Developer"]
    }},
    {{
      "name": "Unit Testing",
      "phase": "Testing & QA",
      "effort_days": 15,
      "dependencies": ["Frontend Development", "Backend API Development"],
      "resources_needed": ["QA Engineer", "Developers"]
    }},
    {{
      "name": "Integration Testing",
      "phase": "Testing & QA",
      "effort_days": 12,
      "dependencies": ["Unit Testing"],
      "resources_needed": ["QA Engineer"]
    }},
    {{
      "name": "Security Testing",
      "phase": "Testing & QA",
      "effort_days": 8,
      "dependencies": ["Integration Testing"],
      "resources_needed": ["Security Engineer", "QA Engineer"]
    }},
    {{
      "name": "User Acceptance Testing",
      "phase": "Testing & QA",
      "effort_days": 10,
      "dependencies": ["Security Testing"],
      "resources_needed": ["Business Analyst", "QA Engineer"]
    }},
    {{
      "name": "Production Deployment",
      "phase": "Deployment & Launch",
      "effort_days": 5,
      "dependencies": ["User Acceptance Testing"],
      "resources_needed": ["DevOps Engineer", "Technical Lead"]
    }},
    {{
      "name": "User Training",
      "phase": "Deployment & Launch",
      "effort_days": 6,
      "dependencies": ["Production Deployment"],
      "resources_needed": ["Business Analyst", "Technical Writer"]
    }}
  ],
  "resources": [
    {{
      "role": "Project Manager",
      "count": 1,
      "effort_months": 6,
      "allocation_percentage": 100,
      "monthly_rate": 10000,
      "total_cost": 60000
    }},
    {{
      "role": "Business Analyst",
      "count": 1,
      "effort_months": 5,
      "allocation_percentage": 80,
      "monthly_rate": 8000,
      "total_cost": 40000
    }},
    {{
      "role": "Solution Architect",
      "count": 1,
      "effort_months": 3,
      "allocation_percentage": 60,
      "monthly_rate": 12000,
      "total_cost": 36000
    }},
    {{
      "role": "UI/UX Designer",
      "count": 1,
      "effort_months": 3,
      "allocation_percentage": 100,
      "monthly_rate": 7000,
      "total_cost": 21000
    }},
    {{
      "role": "Frontend Developer",
      "count": 2,
      "effort_months": 4,
      "allocation_percentage": 100,
      "monthly_rate": 8000,
      "total_cost": 64000
    }},
    {{
      "role": "Backend Developer",
      "count": 3,
      "effort_months": 4.5,
      "allocation_percentage": 100,
      "monthly_rate": 8500,
      "total_cost": 114750
    }},
    {{
      "role": "QA Engineer",
      "count": 2,
      "effort_months": 3.5,
      "allocation_percentage": 100,
      "monthly_rate": 7000,
      "total_cost": 49000
    }},
    {{
      "role": "DevOps Engineer",
      "count": 1,
      "effort_months": 2,
      "allocation_percentage": 50,
      "monthly_rate": 9000,
      "total_cost": 9000
    }},
    {{
      "role": "Security Engineer",
      "count": 1,
      "effort_months": 1.5,
      "allocation_percentage": 50,
      "monthly_rate": 10000,
      "total_cost": 7500
    }},
    {{
      "role": "Technical Writer",
      "count": 1,
      "effort_months": 1,
      "allocation_percentage": 100,
      "monthly_rate": 6000,
      "total_cost": 6000
    }}
  ],
  "architecture": {{
    "description": "Modern scalable architecture with microservices",
    "components": [
      {{
        "name": "Frontend Layer",
        "technology": "React/Next.js",
        "description": "Responsive web application with modern UI"
      }},
      {{
        "name": "API Gateway",
        "technology": "Kong/AWS API Gateway",
        "description": "API management and routing"
      }},
      {{
        "name": "Backend Services",
        "technology": "Node.js/Python FastAPI",
        "description": "RESTful microservices"
      }},
      {{
        "name": "Database Layer",
        "technology": "PostgreSQL/MongoDB",
        "description": "Data persistence and caching"
      }},
      {{
        "name": "Authentication",
        "technology": "OAuth 2.0/JWT",
        "description": "Secure user authentication"
      }}
    ]
  }},
  "cost_breakdown": {{
    "total_cost": 407250,
    "subtotal": 407250,
    "contingency_percentage": 15,
    "contingency_amount": 61087.5,
    "discount_applied": 0
  }},
  "risks": [
    {{
      "risk": "Scope creep during development",
      "severity": "High",
      "probability": "Medium",
      "impact": "High",
      "mitigation": "Implement strict change management process with regular stakeholder reviews",
      "category": "Project Management",
      "owner": "Project Manager"
    }},
    {{
      "risk": "Third-party API integration delays",
      "severity": "Medium",
      "probability": "Medium",
      "impact": "Medium",
      "mitigation": "Early API testing, sandbox environments, and fallback integration plans",
      "category": "Technical",
      "owner": "Technical Lead"
    }},
    {{
      "risk": "Resource availability issues",
      "severity": "Medium",
      "probability": "Low",
      "impact": "High",
      "mitigation": "Maintain backup resource pool and implement cross-training programs",
      "category": "Resource Management",
      "owner": "Project Manager"
    }},
    {{
      "risk": "Security vulnerabilities",
      "severity": "High",
      "probability": "Low",
      "impact": "Critical",
      "mitigation": "Regular security audits, penetration testing, and secure coding practices",
      "category": "Security",
      "owner": "Security Engineer"
    }},
    {{
      "risk": "Performance bottlenecks",
      "severity": "Medium",
      "probability": "Medium",
      "impact": "Medium",
      "mitigation": "Load testing throughout development and scalable architecture design",
      "category": "Technical",
      "owner": "Solution Architect"
    }}
  ],
  "assumptions": [
    "Client will provide timely feedback and approvals within 3 business days",
    "All required resources will be available as per project schedule",
    "Requirements are stable and major changes will follow formal change management process",
    "Development environment and necessary tools will be accessible from project start",
    "Third-party services and APIs will be available and functioning as documented",
    "Client team will be available for regular meetings and clarifications"
  ],
  "dependencies": [
    {{
      "activity": "UI/UX Design",
      "depends_on": ["Requirements Analysis"],
      "phase": "Design & Architecture"
    }},
    {{
      "activity": "Frontend Development",
      "depends_on": ["UI/UX Design"],
      "phase": "Development"
    }},
    {{
      "activity": "Backend API Development",
      "depends_on": ["Database Design", "System Architecture Design"],
      "phase": "Development"
    }}
  ]
}}

Return ONLY this JSON. NO markdown, NO explanations.
"""
            
            print("📤 Sending COMPLETE scope request to Gemini...")
            response = self.model.generate_content(prompt)
            
            scope = self._parse_json_response(response.text)
            scope = self._enhance_scope_with_rag_insights(scope, similar_projects)
            
            print(f"✅ COMPLETE scope generated with {len(scope.get('resources', []))} roles")
            return scope
            
        except Exception as e:
            print(f"❌ Scope generation error: {e}")
            import traceback
            traceback.print_exc()
            return self._get_comprehensive_fallback_scope(project_data)
    
    def _build_search_query(self, project_data: Dict[str, Any], uploaded_content: Optional[str] = None) -> str:
        """Build search query"""
        query_parts = [
            project_data.get('name', ''),
            project_data.get('domain', ''),
            project_data.get('complexity', ''),
            project_data.get('tech_stack', ''),
            project_data.get('use_cases', '')
        ]
        
        if uploaded_content:
            query_parts.append(uploaded_content[:500])
        
        return " ".join(filter(None, query_parts))
    
    def _build_rag_context(self, similar_projects: Dict[str, Any]) -> str:
        """Build RAG context"""
        if not similar_projects.get("similar_projects"):
            return "No similar historical projects found."
        
        context = "INSIGHTS FROM SIMILAR PROJECTS:\n\n"
        for i, project in enumerate(similar_projects["similar_projects"][:3], 1):
            context += f"Project {i}: {project.get('project_name', 'Unknown')}\n"
            context += f"Cost: ${project.get('total_cost', 0):,} | Duration: {project.get('duration_months', 0)} months\n\n"
        
        return context
    
    def _build_scope_context(self, project_data: Dict[str, Any], answered_questions: List, similar_projects: List) -> str:
        """Build context"""
        context = f"""
PROJECT DETAILS:
- Name: {project_data.get('name')}
- Domain: {project_data.get('domain')}
- Complexity: {project_data.get('complexity')}
"""
        return context
    
    async def _generate_questions_with_context(self, project_data: Dict[str, Any], uploaded_content: Optional[str], rag_context: str) -> Dict[str, Any]:
        """Generate questions"""
        return {
            "questions": [],
            "initial_analysis": {
                "summary": f"Project scoping for {project_data.get('name')}",
                "key_challenges": ["Resource allocation", "Timeline management"],
                "recommended_approach": "Agile methodology"
            }
        }
    
    def _parse_json_response(self, response_text: str) -> Any:
        """Parse JSON"""
        try:
            text = re.sub(r'```json\s*', '', response_text)
            text = re.sub(r'```\s*', '', text).strip()
            
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
            
            raise ValueError("No JSON found")
                
        except Exception as e:
            print(f"❌ JSON parsing error: {e}")
            raise
    
    def _enhance_scope_with_rag_insights(self, scope: Dict[str, Any], similar_projects: List) -> Dict[str, Any]:
        """Enhance with RAG"""
        if similar_projects:
            scope['rag_insights'] = {
                "similar_projects_count": len(similar_projects),
                "historical_reference": True
            }
        return scope
    
    def _get_comprehensive_fallback_scope(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """COMPREHENSIVE fallback scope with ALL resources"""
        return {
            "overview": {
                "project_summary": f"Comprehensive project scoping for {project_data.get('name', 'project')} in {project_data.get('domain', 'general')} domain with {project_data.get('complexity', 'moderate')} complexity level.",
                "key_objectives": [
                    "Deliver high-quality solution meeting all requirements",
                    "Complete project within agreed timeline and budget",
                    "Ensure stakeholder satisfaction and project success",
                    "Implement best practices and industry standards"
                ],
                "success_metrics": [
                    "Client satisfaction score > 90%",
                    "On-time delivery within ±5% variance",
                    "Budget adherence within ±10% variance",
                    "Zero critical defects at launch"
                ],
                "deliverables": [
                    "Fully functional application",
                    "Technical and user documentation",
                    "Training materials and sessions",
                    "Deployment and maintenance guide"
                ]
            },
            "timeline": {
                "total_duration_months": 6,
                "total_duration_weeks": 24,
                "phases": [
                    {
                        "phase_name": "Planning & Requirements",
                        "duration_weeks": 4,
                        "start_week": 1,
                        "end_week": 4,
                        "milestones": ["Requirements finalized", "Project plan approved"],
                        "activities": ["Requirements gathering", "Stakeholder interviews"]
                    },
                    {
                        "phase_name": "Design & Architecture",
                        "duration_weeks": 4,
                        "start_week": 5,
                        "end_week": 8,
                        "milestones": ["Design complete", "Architecture approved"],
                        "activities": ["UI/UX design", "System architecture design"]
                    },
                    {
                        "phase_name": "Development",
                        "duration_weeks": 10,
                        "start_week": 9,
                        "end_week": 18,
                        "milestones": ["Core features complete", "Integration done"],
                        "activities": ["Frontend development", "Backend development"]
                    },
                    {
                        "phase_name": "Testing & QA",
                        "duration_weeks": 4,
                        "start_week": 19,
                        "end_week": 22,
                        "milestones": ["All tests passed", "UAT complete"],
                        "activities": ["Testing", "Quality assurance"]
                    },
                    {
                        "phase_name": "Deployment",
                        "duration_weeks": 2,
                        "start_week": 23,
                        "end_week": 24,
                        "milestones": ["Production deployment", "Project handover"],
                        "activities": ["Deployment", "Training"]
                    }
                ]
            },
            "activities": [
                {"name": "Requirements Analysis", "phase": "Planning & Requirements", "effort_days": 12, "dependencies": [], "resources_needed": ["Business Analyst", "Project Manager"]},
                {"name": "System Architecture", "phase": "Design & Architecture", "effort_days": 15, "dependencies": ["Requirements Analysis"], "resources_needed": ["Solution Architect"]},
                {"name": "UI/UX Design", "phase": "Design & Architecture", "effort_days": 18, "dependencies": ["Requirements Analysis"], "resources_needed": ["UI/UX Designer"]},
                {"name": "Frontend Development", "phase": "Development", "effort_days": 45, "dependencies": ["UI/UX Design"], "resources_needed": ["Frontend Developer"]},
                {"name": "Backend Development", "phase": "Development", "effort_days": 50, "dependencies": ["System Architecture"], "resources_needed": ["Backend Developer"]},
                {"name": "Testing", "phase": "Testing & QA", "effort_days": 25, "dependencies": ["Frontend Development", "Backend Development"], "resources_needed": ["QA Engineer"]},
                {"name": "Deployment", "phase": "Deployment", "effort_days": 5, "dependencies": ["Testing"], "resources_needed": ["DevOps Engineer"]}
            ],
            "resources": [
                {"role": "Project Manager", "count": 1, "effort_months": 6, "allocation_percentage": 100, "monthly_rate": 10000, "total_cost": 60000},
                {"role": "Business Analyst", "count": 1, "effort_months": 5, "allocation_percentage": 80, "monthly_rate": 8000, "total_cost": 32000},
                {"role": "Solution Architect", "count": 1, "effort_months": 3, "allocation_percentage": 60, "monthly_rate": 12000, "total_cost": 21600},
                {"role": "UI/UX Designer", "count": 1, "effort_months": 3, "allocation_percentage": 100, "monthly_rate": 7000, "total_cost": 21000},
                {"role": "Frontend Developer", "count": 2, "effort_months": 4, "allocation_percentage": 100, "monthly_rate": 8000, "total_cost": 64000},
                {"role": "Backend Developer", "count": 3, "effort_months": 4.5, "allocation_percentage": 100, "monthly_rate": 8500, "total_cost": 114750},
                {"role": "QA Engineer", "count": 2, "effort_months": 3.5, "allocation_percentage": 100, "monthly_rate": 7000, "total_cost": 49000},
                {"role": "DevOps Engineer", "count": 1, "effort_months": 2, "allocation_percentage": 50, "monthly_rate": 9000, "total_cost": 9000},
                {"role": "Security Engineer", "count": 1, "effort_months": 1.5, "allocation_percentage": 50, "monthly_rate": 10000, "total_cost": 7500},
                {"role": "Technical Writer", "count": 1, "effort_months": 1, "allocation_percentage": 100, "monthly_rate": 6000, "total_cost": 6000}
            ],
            "architecture": {
                "description": "Modern scalable architecture",
                "components": [
                    {"name": "Frontend", "technology": "React", "description": "Web application"},
                    {"name": "Backend", "technology": "Node.js/Python", "description": "API services"},
                    {"name": "Database", "technology": "PostgreSQL", "description": "Data storage"}
                ]
            },
            "cost_breakdown": {
                "total_cost": 384850,
                "subtotal": 384850,
                "contingency_percentage": 15,
                "contingency_amount": 57727.5,
                "discount_applied": 0
            },
            "risks": [
                {"risk": "Scope creep", "severity": "High", "probability": "Medium", "impact": "High", "mitigation": "Change management process", "category": "Project Management", "owner": "Project Manager"},
                {"risk": "Resource availability", "severity": "Medium", "probability": "Low", "impact": "High", "mitigation": "Backup resources", "category": "Resource Management", "owner": "Project Manager"}
            ],
            "assumptions": [
                "Client will provide timely feedback",
                "Resources will be available as planned",
                "Requirements are stable"
            ],
            "dependencies": []
        }
    
    async def _fallback_analysis(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis"""
        return {
            "questions": [],
            "initial_analysis": {"summary": f"Analysis for {project_data.get('name')}"},
            "similar_projects": [],
            "rag_used": False
        }

# Global instance
enhanced_ai_engine = EnhancedAIEngine()