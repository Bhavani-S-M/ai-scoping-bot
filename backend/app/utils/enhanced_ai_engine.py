# backend/app/utils/enhanced_ai_engine.py
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
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def analyze_project_with_rag(self, project_data: Dict[str, Any], uploaded_content: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced project analysis with RAG - FIXED VERSION"""
        try:
            print(f"🔍 Starting RAG analysis for project: {project_data.get('name')}")
            
            # Build search query
            search_query = self._build_search_query(project_data, uploaded_content)
            print(f"📝 Search query: {search_query[:100]}...")
            
            # Search similar projects with domain filter
            filters = {"domain": project_data.get('domain')} if project_data.get('domain') else None
            similar_projects = await rag_engine.search_similar_projects(
                query=search_query, 
                filters=filters,
                n_results=3
            )
            
            print(f"📊 Found {len(similar_projects.get('similar_projects', []))} similar projects")
            
            # Generate questions with RAG context
            rag_context = self._build_rag_context(similar_projects)
            questions_result = await self._generate_questions_with_context(project_data, uploaded_content, rag_context)
            
            return {
                **questions_result,
                "similar_projects": similar_projects.get("similar_projects", []),
                "rag_used": len(similar_projects.get("similar_projects", [])) > 0
            }
            
        except Exception as e:
            print(f"❌ RAG analysis error: {e}")
            import traceback
            traceback.print_exc()
            return await self._fallback_analysis(project_data)
    
    async def generate_scope_with_rag(self, 
                                    project_data: Dict[str, Any], 
                                    answered_questions: List[Dict[str, Any]] = None,
                                    similar_projects: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate scope using RAG-enhanced context - FIXED VERSION"""
        try:
            print(f"🎯 Generating scope for: {project_data.get('name')}")
            
            # Build comprehensive context
            context = self._build_scope_context(project_data, answered_questions or [], similar_projects or [])
            
            prompt = f"""
You are an expert project manager. Generate a COMPREHENSIVE project scope.

{context}

CRITICAL: Return ONLY a valid JSON object. NO markdown, NO backticks, NO extra text.

Generate this exact structure:

{{
  "overview": {{
    "project_summary": "A detailed 3-4 sentence summary of the project",
    "key_objectives": ["Objective 1", "Objective 2", "Objective 3"],
    "success_metrics": ["Metric 1", "Metric 2", "Metric 3"],
    "deliverables": ["Deliverable 1", "Deliverable 2"]
  }},
  "timeline": {{
    "total_duration_months": 6,
    "total_duration_weeks": 24,
    "phases": [
      {{
        "phase_name": "Phase 1: Planning & Design",
        "duration_weeks": 4,
        "start_week": 1,
        "end_week": 4,
        "milestones": ["Requirements finalized", "Design approved"],
        "activities": ["Requirements gathering", "Architecture design"]
      }},
      {{
        "phase_name": "Phase 2: Development",
        "duration_weeks": 12,
        "start_week": 5,
        "end_week": 16,
        "milestones": ["Core features complete", "Integration done"],
        "activities": ["Frontend development", "Backend development", "API integration"]
      }},
      {{
        "phase_name": "Phase 3: Testing & Deployment",
        "duration_weeks": 4,
        "start_week": 17,
        "end_week": 20,
        "milestones": ["Testing complete", "Production deployment"],
        "activities": ["Quality assurance", "User acceptance testing", "Deployment"]
      }}
    ]
  }},
  "activities": [
    {{
      "name": "Requirements Analysis",
      "phase": "Planning & Design",
      "effort_days": 10,
      "dependencies": [],
      "resources_needed": ["Business Analyst", "Project Manager"]
    }},
    {{
      "name": "UI/UX Design",
      "phase": "Planning & Design",
      "effort_days": 15,
      "dependencies": ["Requirements Analysis"],
      "resources_needed": ["UI/UX Designer"]
    }},
    {{
      "name": "Database Design",
      "phase": "Planning & Design",
      "effort_days": 8,
      "dependencies": ["Requirements Analysis"],
      "resources_needed": ["Database Architect"]
    }},
    {{
      "name": "Frontend Development",
      "phase": "Development",
      "effort_days": 40,
      "dependencies": ["UI/UX Design"],
      "resources_needed": ["Frontend Developer"]
    }},
    {{
      "name": "Backend Development",
      "phase": "Development",
      "effort_days": 45,
      "dependencies": ["Database Design"],
      "resources_needed": ["Backend Developer"]
    }},
    {{
      "name": "API Integration",
      "phase": "Development",
      "effort_days": 20,
      "dependencies": ["Frontend Development", "Backend Development"],
      "resources_needed": ["Full Stack Developer"]
    }},
    {{
      "name": "Unit Testing",
      "phase": "Testing & Deployment",
      "effort_days": 15,
      "dependencies": ["API Integration"],
      "resources_needed": ["QA Engineer"]
    }},
    {{
      "name": "Integration Testing",
      "phase": "Testing & Deployment",
      "effort_days": 10,
      "dependencies": ["Unit Testing"],
      "resources_needed": ["QA Engineer"]
    }},
    {{
      "name": "User Acceptance Testing",
      "phase": "Testing & Deployment",
      "effort_days": 10,
      "dependencies": ["Integration Testing"],
      "resources_needed": ["QA Engineer", "Business Analyst"]
    }},
    {{
      "name": "Deployment",
      "phase": "Testing & Deployment",
      "effort_days": 5,
      "dependencies": ["User Acceptance Testing"],
      "resources_needed": ["DevOps Engineer"]
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
      "effort_months": 3,
      "allocation_percentage": 50,
      "monthly_rate": 8000,
      "total_cost": 24000
    }},
    {{
      "role": "UI/UX Designer",
      "count": 1,
      "effort_months": 2,
      "allocation_percentage": 100,
      "monthly_rate": 7000,
      "total_cost": 14000
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
      "count": 2,
      "effort_months": 4,
      "allocation_percentage": 100,
      "monthly_rate": 8000,
      "total_cost": 64000
    }},
    {{
      "role": "QA Engineer",
      "count": 1,
      "effort_months": 3,
      "allocation_percentage": 100,
      "monthly_rate": 7000,
      "total_cost": 21000
    }},
    {{
      "role": "DevOps Engineer",
      "count": 1,
      "effort_months": 2,
      "allocation_percentage": 50,
      "monthly_rate": 9000,
      "total_cost": 9000
    }}
  ],
  "architecture": {{
    "description": "Modern three-tier architecture with microservices",
    "components": [
      {{
        "name": "Frontend",
        "technology": "React/Next.js",
        "description": "Responsive web application"
      }},
      {{
        "name": "Backend API",
        "technology": "Node.js/FastAPI",
        "description": "RESTful API services"
      }},
      {{
        "name": "Database",
        "technology": "PostgreSQL",
        "description": "Relational database"
      }}
    ]
  }},
  "cost_breakdown": {{
    "total_cost": 256000,
    "subtotal": 256000,
    "contingency_percentage": 15,
    "contingency_amount": 38400,
    "discount_applied": 0
  }},
  "risks": [
    {{
      "risk": "Scope creep during development",
      "severity": "High",
      "probability": "Medium",
      "impact": "High",
      "mitigation": "Strict change management process and regular stakeholder reviews",
      "category": "Project Management",
      "owner": "Project Manager"
    }},
    {{
      "risk": "Third-party API integration delays",
      "severity": "Medium",
      "probability": "Medium",
      "impact": "Medium",
      "mitigation": "Early API testing and fallback integration plans",
      "category": "Technical",
      "owner": "Technical Lead"
    }},
    {{
      "risk": "Resource availability issues",
      "severity": "Medium",
      "probability": "Low",
      "impact": "High",
      "mitigation": "Maintain backup resource pool and cross-training",
      "category": "Resource Management",
      "owner": "Project Manager"
    }}
  ],
  "assumptions": [
    "Client will provide timely feedback and approvals",
    "All required resources will be available as planned",
    "Requirements are stable and major changes will follow change management process"
  ],
  "dependencies": [
    {{
      "activity": "UI/UX Design",
      "depends_on": ["Requirements Analysis"],
      "phase": "Planning & Design"
    }}
  ]
}}

Return ONLY this JSON object. NO other text.
"""
            
            print("📤 Sending prompt to Gemini...")
            response = self.model.generate_content(prompt)
            print("📥 Received response from Gemini")
            
            scope = self._parse_json_response(response.text)
            print("✅ Successfully parsed scope JSON")
            
            # Enhance with RAG insights
            scope = self._enhance_scope_with_rag_insights(scope, similar_projects)
            
            return scope
            
        except Exception as e:
            print(f"❌ Scope generation error: {e}")
            import traceback
            traceback.print_exc()
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
            query_parts.append(uploaded_content[:500])
        
        return " ".join(filter(None, query_parts))
    
    def _build_rag_context(self, similar_projects: Dict[str, Any]) -> str:
        """Build context from similar projects"""
        if not similar_projects.get("similar_projects"):
            return "No similar historical projects found."
        
        context = "INSIGHTS FROM SIMILAR HISTORICAL PROJECTS:\n\n"
        
        for i, project in enumerate(similar_projects["similar_projects"][:3], 1):
            context += f"Project {i}: {project.get('project_name', 'Unknown')}\n"
            context += f"Domain: {project.get('domain', 'Unknown')} | Complexity: {project.get('complexity', 'Unknown')}\n"
            context += f"Cost: ${project.get('total_cost', 0):,} | Duration: {project.get('duration_months', project.get('duration', 0))} months\n"
            context += f"Similarity: {project.get('similarity_score', 0):.2f}\n"
            
            if project.get('key_insights'):
                context += "Key Insights:\n"
                for insight in project['key_insights']:
                    context += f"  • {insight}\n"
            elif project.get('lessons_learned'):
                context += f"Lessons: {project['lessons_learned']}\n"
            
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
- Compliance: {project_data.get('compliance')}
- Duration: {project_data.get('duration')}
"""
        
        if answered_questions:
            context += "\nCLARIFYING ANSWERS:\n"
            for q in answered_questions:
                context += f"Q: {q.get('question')}\nA: {q.get('answer')}\n\n"
        
        if similar_projects:
            context += "\nHISTORICAL PROJECT INSIGHTS:\n"
            for project in similar_projects[:2]:
                context += f"• Similar project '{project.get('project_name', 'Unknown')}': "
                context += f"{project.get('duration_months', project.get('duration', 0))} months, "
                context += f"${project.get('total_cost', 0):,}\n"
                
                insights = project.get('key_insights', []) or [project.get('lessons_learned', '')]
                for insight in insights[:2]:
                    if insight:
                        context += f"  - {insight}\n"
        
        return context
    
    async def _generate_questions_with_context(self, 
                                            project_data: Dict[str, Any], 
                                            uploaded_content: Optional[str],
                                            rag_context: str) -> Dict[str, Any]:
        """Generate questions with RAG context - FIXED VERSION"""
        
        prompt = f"""
You are an expert project consultant. Generate 5-7 clarifying questions for this project.

PROJECT INFO:
- Name: {project_data.get('name')}
- Domain: {project_data.get('domain')}
- Complexity: {project_data.get('complexity')}
- Tech Stack: {project_data.get('tech_stack')}
- Use Cases: {project_data.get('use_cases')}

{rag_context}

CRITICAL: Return ONLY a valid JSON array. NO markdown, NO backticks, NO extra text.

Generate this exact structure:

[
  {{
    "id": "q1",
    "category": "Technical Requirements",
    "question": "What are the specific security requirements for user authentication?",
    "importance": "high",
    "suggested_answers": ["OAuth 2.0", "JWT tokens", "Session-based", "Multi-factor authentication"]
  }},
  {{
    "id": "q2",
    "category": "Business Requirements",
    "question": "What is the expected user base and scale?",
    "importance": "high",
    "suggested_answers": ["< 1000 users", "1K-10K users", "10K-100K users", "> 100K users"]
  }},
  {{
    "id": "q3",
    "category": "Timeline & Resources",
    "question": "Are there any specific deadlines or milestones?",
    "importance": "high",
    "suggested_answers": ["Hard launch date", "Flexible timeline", "Phased rollout"]
  }},
  {{
    "id": "q4",
    "category": "Compliance & Security",
    "question": "What compliance standards must be met?",
    "importance": "medium",
    "suggested_answers": ["GDPR", "HIPAA", "PCI-DSS", "None specific"]
  }},
  {{
    "id": "q5",
    "category": "Technical Requirements",
    "question": "What is the preferred deployment environment?",
    "importance": "medium",
    "suggested_answers": ["Cloud (AWS/Azure/GCP)", "On-premise", "Hybrid"]
  }}
]

Return ONLY this JSON array. NO other text.
"""
        
        try:
            print("📤 Sending questions prompt to Gemini...")
            response = self.model.generate_content(prompt)
            print("📥 Received questions response")
            
            questions = self._parse_json_response(response.text)
            print(f"✅ Successfully parsed {len(questions)} questions")
            
            return {
                "questions": questions,
                "initial_analysis": {
                    "summary": f"Project scoping for {project_data.get('name')} in {project_data.get('domain')} domain",
                    "key_challenges": ["Resource allocation", "Timeline management", "Quality assurance"],
                    "recommended_approach": "Agile methodology with 2-week sprints",
                    "estimated_complexity": project_data.get('complexity', 'medium'),
                    "missing_information": ["Detailed requirements", "Budget constraints"]
                }
            }
            
        except Exception as e:
            print(f"❌ Questions generation error: {e}")
            return self._get_fallback_questions()
    
    def _parse_json_response(self, response_text: str) -> Any:
        """Parse JSON from AI response - IMPROVED VERSION"""
        try:
            print(f"🔍 Parsing response (length: {len(response_text)})")
            print(f"📝 First 200 chars: {response_text[:200]}")
            
            # Remove markdown code blocks
            text = re.sub(r'```json\s*', '', response_text)
            text = re.sub(r'```\s*', '', text).strip()
            
            # Remove any text before first { or [
            start_brace = text.find('{')
            start_bracket = text.find('[')
            
            if start_brace == -1 and start_bracket == -1:
                raise ValueError("No JSON object or array found in response")
            
            # Use whichever comes first
            if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
                start = start_brace
                # Find matching closing brace
                brace_count = 0
                end = start
                for i in range(start, len(text)):
                    if text[i] == '{':
                        brace_count += 1
                    elif text[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break
            else:
                start = start_bracket
                # Find matching closing bracket
                bracket_count = 0
                end = start
                for i in range(start, len(text)):
                    if text[i] == '[':
                        bracket_count += 1
                    elif text[i] == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end = i + 1
                            break
            
            json_str = text[start:end]
            print(f"✂️ Extracted JSON (length: {len(json_str)})")
            
            result = json.loads(json_str)
            print("✅ Successfully parsed JSON")
            return result
            
        except Exception as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"📄 Full response:\n{response_text}")
            raise
    
    def _enhance_scope_with_rag_insights(self, scope: Dict[str, Any], similar_projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance scope with insights from similar projects"""
        if not similar_projects:
            return scope
        
        most_similar = similar_projects[0]
        
        # Add RAG insights section
        scope['rag_insights'] = {
            "similar_projects_count": len(similar_projects),
            "most_similar_project": most_similar.get('project_name', 'Unknown'),
            "similarity_score": most_similar.get('similarity_score', 0),
            "historical_reference": True,
            "insights_applied": [
                f"Timeline adjusted based on {most_similar.get('project_name', 'historical')} project",
                f"Resource allocation informed by similar {most_similar.get('domain', '')} projects",
                "Cost estimates validated against historical data"
            ]
        }
        
        return scope
    
    def _get_fallback_questions(self) -> Dict[str, Any]:
        """Fallback questions when AI fails"""
        return {
            "questions": [
                {
                    "id": "q1",
                    "category": "Technical Requirements",
                    "question": "What are your specific technical requirements?",
                    "importance": "high",
                    "suggested_answers": ["Web application", "Mobile app", "Desktop software", "API/Backend"]
                },
                {
                    "id": "q2",
                    "category": "Business Requirements",
                    "question": "What is your target user base size?",
                    "importance": "high",
                    "suggested_answers": ["< 1000", "1K-10K", "10K-100K", "> 100K"]
                },
                {
                    "id": "q3",
                    "category": "Timeline & Resources",
                    "question": "What is your target launch date?",
                    "importance": "high",
                    "suggested_answers": ["< 3 months", "3-6 months", "6-12 months", "> 12 months"]
                }
            ],
            "initial_analysis": {
                "summary": "Initial analysis pending detailed information",
                "key_challenges": ["Requirements clarification needed"],
                "recommended_approach": "Agile methodology",
                "estimated_complexity": "medium",
                "missing_information": ["Detailed requirements"]
            }
        }
    
    def _get_fallback_scope(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback scope generation"""
        return {
            "overview": {
                "project_summary": f"Project scoping for {project_data.get('name', 'Unknown')} in {project_data.get('domain', 'Unknown')} domain",
                "key_objectives": ["Deliver quality solution", "Meet timeline", "Stay within budget"],
                "success_metrics": ["Client satisfaction", "On-time delivery", "Budget adherence"],
                "deliverables": ["Working software", "Documentation", "Training materials"]
            },
            "timeline": {
                "total_duration_months": 6,
                "total_duration_weeks": 24,
                "phases": [
                    {
                        "phase_name": "Planning",
                        "duration_weeks": 4,
                        "start_week": 1,
                        "end_week": 4,
                        "milestones": ["Requirements complete"],
                        "activities": ["Requirements gathering"]
                    }
                ]
            },
            "activities": [
                {
                    "name": "Requirements Analysis",
                    "phase": "Planning",
                    "effort_days": 10,
                    "dependencies": [],
                    "resources_needed": ["Business Analyst"]
                }
            ],
            "resources": [
                {
                    "role": "Project Manager",
                    "count": 1,
                    "effort_months": 6,
                    "allocation_percentage": 100,
                    "monthly_rate": 10000,
                    "total_cost": 60000
                }
            ],
            "architecture": {
                "description": "Standard architecture pending detailed requirements",
                "components": []
            },
            "cost_breakdown": {
                "total_cost": 60000,
                "subtotal": 60000,
                "contingency_percentage": 15,
                "contingency_amount": 9000,
                "discount_applied": 0
            },
            "risks": [
                {
                    "risk": "Incomplete requirements",
                    "severity": "High",
                    "probability": "Medium",
                    "impact": "High",
                    "mitigation": "Detailed discovery phase",
                    "category": "Requirements",
                    "owner": "Project Manager"
                }
            ],
            "assumptions": [
                "Client will provide timely feedback",
                "Resources will be available as needed"
            ],
            "dependencies": []
        }
    
    async def _fallback_analysis(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when RAG fails"""
        return {
            **self._get_fallback_questions(),
            "similar_projects": [],
            "rag_used": False
        }

# Global instance
enhanced_ai_engine = EnhancedAIEngine()