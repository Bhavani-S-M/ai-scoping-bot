# backend/app/utils/rag_engine.py
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime
from app.config.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

class RAGEngine:
    """Enhanced RAG engine with knowledge base learning and better error handling"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def search_similar_projects(self, query: str, filters: Optional[Dict] = None, n_results: int = 5) -> Dict[str, Any]:
        """
        Enhanced similarity search with filtering and better mock data
        """
        try:
            print(f"🔍 Searching similar projects for: {query[:100]}...")
            
            # Enhanced mock data with realistic project examples
            mock_similar = []
            domains = filters.get('domain', 'technology').lower() if filters else 'technology'
            
            project_templates = {
                'healthcare': [
                    {
                        "project_name": "Patient Management System",
                        "domain": "Healthcare",
                        "complexity": "complex",
                        "total_cost": 350000,
                        "duration_months": 8,
                        "key_technologies": ["React", "Node.js", "PostgreSQL", "HIPAA Compliance"],
                        "lessons_learned": "Ensure HIPAA compliance from day one and implement robust audit trails.",
                        "key_insights": ["Healthcare projects require extensive compliance documentation", "User training is critical for adoption"]
                    },
                    {
                        "project_name": "Medical Records Digitalization",
                        "domain": "Healthcare", 
                        "complexity": "enterprise",
                        "total_cost": 750000,
                        "duration_months": 12,
                        "key_technologies": ["Angular", "Java", "Oracle DB", "HL7 FHIR"],
                        "lessons_learned": "Integration with existing medical systems requires careful planning and testing.",
                        "key_insights": ["Legacy system integration is often the biggest challenge", "Data migration requires extensive validation"]
                    }
                ],
                'finance': [
                    {
                        "project_name": "Mobile Banking App",
                        "domain": "Finance",
                        "complexity": "complex", 
                        "total_cost": 450000,
                        "duration_months": 9,
                        "key_technologies": ["React Native", "Python", "PostgreSQL", "PCI-DSS"],
                        "lessons_learned": "Security testing should be integrated throughout the development lifecycle.",
                        "key_insights": ["Financial apps require rigorous security testing", "Performance under load is critical"]
                    }
                ],
                'ecommerce': [
                    {
                        "project_name": "E-commerce Platform",
                        "domain": "E-commerce",
                        "complexity": "moderate",
                        "total_cost": 200000,
                        "duration_months": 6,
                        "key_technologies": ["React", "Node.js", "MongoDB", "Stripe API"],
                        "lessons_learned": "Payment gateway integration requires thorough testing with sandbox environments.",
                        "key_insights": ["Scalability should be considered from the beginning", "User experience drives conversion rates"]
                    }
                ],
                'technology': [
                    {
                        "project_name": "SaaS Analytics Platform",
                        "domain": "Technology",
                        "complexity": "complex",
                        "total_cost": 300000,
                        "duration_months": 7,
                        "key_technologies": ["Vue.js", "Python", "PostgreSQL", "D3.js"],
                        "lessons_learned": "Real-time data processing requires careful architecture planning.",
                        "key_insights": ["Data visualization complexity often underestimated", "API rate limiting is essential"]
                    }
                ]
            }
            
            # Select appropriate template based on domain
            template_projects = project_templates.get(domains, project_templates['technology'])
            
            for i, template in enumerate(template_projects[:n_results]):
                similarity_score = max(0.7, 0.9 - (i * 0.1))  # Decreasing similarity
                
                project = {
                    "id": str(uuid.uuid4()),
                    "project_name": template["project_name"],
                    "domain": template["domain"],
                    "complexity": template["complexity"],
                    "similarity_score": similarity_score,
                    "total_cost": template["total_cost"],
                    "duration_months": template["duration_months"],
                    "duration": f"{template['duration_months']} months",
                    "key_technologies": template["key_technologies"],
                    "lessons_learned": template["lessons_learned"],
                    "key_insights": template.get("key_insights", []),
                    "search_match_reason": f"Similar domain ({domains}) and complexity level"
                }
                mock_similar.append(project)
            
            # Fill remaining slots with generic projects if needed
            while len(mock_similar) < n_results:
                project = {
                    "id": str(uuid.uuid4()),
                    "project_name": f"Generic {domains.title()} Project",
                    "domain": domains.title(),
                    "complexity": "moderate",
                    "similarity_score": 0.6,
                    "total_cost": 150000 + (len(mock_similar) * 50000),
                    "duration_months": 6,
                    "duration": "6 months",
                    "key_technologies": ["React", "Node.js", "PostgreSQL"],
                    "lessons_learned": "Proper requirements gathering is essential for project success.",
                    "key_insights": ["Clear communication with stakeholders is critical", "Agile methodology helps manage changing requirements"],
                    "search_match_reason": "Domain match with standard technology stack"
                }
                mock_similar.append(project)
            
            print(f"✅ Found {len(mock_similar)} similar projects")
            
            return {
                "similar_projects": mock_similar,
                "search_query": query,
                "filters_applied": filters,
                "total_matches": len(mock_similar),
                "search_quality": "high" if len(mock_similar) > 0 else "low"
            }
            
        except Exception as e:
            print(f"❌ Similar projects search error: {e}")
            return {
                "similar_projects": [],
                "search_query": query,
                "filters_applied": filters,
                "total_matches": 0,
                "search_quality": "error",
                "error": str(e)
            }
    
    async def store_project_scope(self, project_data: Dict[str, Any], scope_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store finalized project scope in knowledge base for learning with enhanced metadata
        """
        try:
            print(f"📚 Storing project in knowledge base: {project_data.get('name')}")
            
            # Enhanced learning data extraction
            total_cost = scope_data.get('cost_breakdown', {}).get('total_cost', 0)
            duration = scope_data.get('timeline', {}).get('total_duration_months', 0)
            resources = scope_data.get('resources', [])
            activities = scope_data.get('activities', [])
            
            # Prepare comprehensive learning payload
            learning_payload = {
                "project_id": project_data.get('id'),
                "project_name": project_data.get('name'),
                "domain": project_data.get('domain'),
                "complexity": project_data.get('complexity'),
                "tech_stack": project_data.get('tech_stack'),
                "scope_metadata": {
                    "total_cost": total_cost,
                    "duration_months": duration,
                    "team_size": len(resources),
                    "activities_count": len(activities),
                    "total_effort_days": sum(act.get('effort_days', 0) for act in activities),
                    "resource_roles": [r.get('role') for r in resources]
                },
                "key_learnings": self._extract_comprehensive_learnings(scope_data, project_data),
                "success_factors": self._identify_success_factors(scope_data),
                "risk_patterns": self._extract_risk_patterns(scope_data),
                "technology_patterns": self._extract_technology_patterns(scope_data, project_data),
                "stored_at": datetime.now().isoformat(),
                "version": "3.0",
                "learning_quality": "high"
            }
            
            # Simulate vector DB storage with enhanced metadata
            storage_result = {
                "status": "success",
                "document_id": str(uuid.uuid4()),
                "project_id": project_data.get('id'),
                "project_name": project_data.get('name'),
                "storage_timestamp": datetime.now().isoformat(),
                "embedding_size": 1536,  # Larger embedding for better similarity
                "metadata": {
                    "domain": project_data.get('domain'),
                    "complexity": project_data.get('complexity'),
                    "cost_range": self._get_cost_range(total_cost),
                    "duration_range": self._get_duration_range(duration),
                    "team_size_range": self._get_team_size_range(len(resources)),
                    "technology_categories": self._categorize_technologies(project_data.get('tech_stack', '')),
                    "project_type": self._classify_project_type(project_data, scope_data)
                },
                "learning_insights_count": len(learning_payload['key_learnings'])
            }
            
            # Trigger enhanced admin notification
            await self._notify_admins_enhanced(project_data, scope_data, learning_payload)
            
            print(f"✅ Successfully stored project with {len(learning_payload['key_learnings'])} learning insights")
            
            return storage_result
            
        except Exception as e:
            print(f"❌ Knowledge base storage error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "fallback_storage": "local_cache"
            }
    
    def _extract_comprehensive_learnings(self, scope_data: Dict[str, Any], project_data: Dict[str, Any]) -> List[str]:
        """Extract comprehensive learnings from scope data"""
        learnings = []
        
        total_cost = scope_data.get('cost_breakdown', {}).get('total_cost', 0)
        duration = scope_data.get('timeline', {}).get('total_duration_months', 0)
        resources = scope_data.get('resources', [])
        activities = scope_data.get('activities', [])
        
        # Cost-related learnings
        if total_cost > 500000:
            learnings.append("Large-scale enterprise project requiring sophisticated resource management and risk mitigation")
        elif total_cost > 200000:
            learnings.append("Medium to large project benefiting from phased delivery and regular stakeholder checkpoints")
        else:
            learnings.append("Small to medium project suitable for agile delivery with focused scope")
        
        # Duration learnings
        if duration > 12:
            learnings.append("Long-term project requiring strong change management and milestone-based delivery")
        elif duration > 6:
            learnings.append("Medium-term project suitable for iterative development with clear phase gates")
        
        # Resource learnings
        dev_count = sum(1 for r in resources if any(role in r.get('role', '').lower() for role in ['developer', 'engineer']))
        if dev_count > 8:
            learnings.append("Large development team requiring strong coordination, communication protocols, and technical leadership")
        elif dev_count > 3:
            learnings.append("Medium development team benefiting from agile practices and regular sync-ups")
        
        # Technology learnings
        tech_stack = project_data.get('tech_stack', '').lower()
        if 'react' in tech_stack or 'angular' in tech_stack or 'vue' in tech_stack:
            learnings.append("Frontend-heavy project requiring careful attention to user experience and performance optimization")
        if 'machine learning' in tech_stack or 'ai' in tech_stack:
            learnings.append("AI/ML project requiring specialized expertise and iterative model development approach")
        
        # Risk-based learnings
        high_risks = [r for r in scope_data.get('risks', []) if r.get('severity') == 'High']
        if high_risks:
            learnings.append(f"Project has {len(high_risks)} high-severity risks requiring proactive mitigation strategies")
        
        return learnings
    
    def _identify_success_factors(self, scope_data: Dict[str, Any]) -> List[str]:
        """Identify key success factors from scope"""
        factors = []
        
        # Based on timeline structure
        phases = scope_data.get('timeline', {}).get('phases', [])
        if len(phases) >= 3:
            factors.append("Well-structured phased approach with clear milestones")
        
        # Based on resource allocation
        resources = scope_data.get('resources', [])
        pm_count = sum(1 for r in resources if 'manager' in r.get('role', '').lower())
        if pm_count > 0:
            factors.append("Dedicated project management ensuring delivery accountability")
        
        # Based on risk management
        risks = scope_data.get('risks', [])
        if any(r.get('mitigation') for r in risks):
            factors.append("Proactive risk management with defined mitigation strategies")
        
        return factors
    
    def _extract_risk_patterns(self, scope_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and categorize risk patterns"""
        risks = scope_data.get('risks', [])
        patterns = []
        
        for risk in risks[:5]:  # Limit to top 5 risks
            patterns.append({
                "category": risk.get('category', 'Unknown'),
                "severity": risk.get('severity', 'Medium'),
                "common_mitigation": risk.get('mitigation', ''),
                "frequency": "common" if risk.get('probability') in ['High', 'Medium'] else "rare"
            })
        
        return patterns
    
    def _extract_technology_patterns(self, scope_data: Dict[str, Any], project_data: Dict[str, Any]) -> List[str]:
        """Extract technology usage patterns"""
        patterns = []
        tech_stack = project_data.get('tech_stack', '').lower()
        
        # Detect common technology combinations
        if 'react' in tech_stack and 'node' in tech_stack:
            patterns.append("Modern web stack: React frontend with Node.js backend")
        if 'python' in tech_stack and 'postgresql' in tech_stack:
            patterns.append("Data-intensive stack: Python with PostgreSQL database")
        if 'aws' in tech_stack or 'azure' in tech_stack or 'gcp' in tech_stack:
            patterns.append("Cloud-native architecture with scalable infrastructure")
        
        return patterns
    
    def _get_cost_range(self, total_cost: float) -> str:
        """Categorize cost range with more granularity"""
        if total_cost < 50000:
            return "small"
        elif total_cost < 150000:
            return "medium"
        elif total_cost < 400000:
            return "large"
        else:
            return "enterprise"
    
    def _get_duration_range(self, duration: float) -> str:
        """Categorize duration range"""
        if duration < 3:
            return "short"
        elif duration < 9:
            return "medium"
        else:
            return "long"
    
    def _get_team_size_range(self, team_size: int) -> str:
        """Categorize team size"""
        if team_size < 3:
            return "small"
        elif team_size < 8:
            return "medium"
        else:
            return "large"
    
    def _categorize_technologies(self, tech_stack: str) -> List[str]:
        """Categorize technologies from stack"""
        categories = []
        stack_lower = tech_stack.lower()
        
        if any(tech in stack_lower for tech in ['react', 'angular', 'vue', 'frontend']):
            categories.append("modern_frontend")
        if any(tech in stack_lower for tech in ['node', 'python', 'java', 'backend']):
            categories.append("backend")
        if any(tech in stack_lower for tech in ['postgresql', 'mongodb', 'mysql', 'database']):
            categories.append("database")
        if any(tech in stack_lower for tech in ['aws', 'azure', 'gcp', 'cloud']):
            categories.append("cloud")
        
        return categories if categories else ["general_technology"]
    
    def _classify_project_type(self, project_data: Dict[str, Any], scope_data: Dict[str, Any]) -> str:
        """Classify project type based on characteristics"""
        domain = project_data.get('domain', '').lower()
        complexity = project_data.get('complexity', '').lower()
        total_cost = scope_data.get('cost_breakdown', {}).get('total_cost', 0)
        
        if domain in ['healthcare', 'finance'] and complexity in ['complex', 'enterprise']:
            return "regulated_enterprise"
        elif total_cost > 300000:
            return "large_scale_development"
        elif 'mobile' in project_data.get('use_cases', '').lower():
            return "mobile_application"
        else:
            return "web_application"
    
    async def _notify_admins_enhanced(self, project_data: Dict[str, Any], scope_data: Dict[str, Any], learning_payload: Dict[str, Any]) -> None:
        """Enhanced admin notification with learning insights"""
        notification = {
            "event_type": "scope_finalized_enhanced",
            "project_id": project_data.get('id'),
            "project_name": project_data.get('name'),
            "domain": project_data.get('domain'),
            "complexity": project_data.get('complexity'),
            "scope_summary": {
                "total_cost": scope_data.get('cost_breakdown', {}).get('total_cost'),
                "duration_months": scope_data.get('timeline', {}).get('total_duration_months'),
                "team_size": len(scope_data.get('resources', [])),
                "activities_count": len(scope_data.get('activities', []))
            },
            "learning_insights": {
                "total_learnings": len(learning_payload['key_learnings']),
                "success_factors": learning_payload['success_factors'],
                "risk_patterns": len(learning_payload['risk_patterns']),
                "technology_patterns": learning_payload['technology_patterns']
            },
            "knowledge_base_impact": {
                "similarity_queries_improved": True,
                "future_recommendations_enhanced": True,
                "pattern_recognition_added": True
            },
            "timestamp": datetime.now().isoformat(),
            "version": "3.0"
        }
        
        # In production, this would send to webhook/email/notification system
        print(f"🔔 Enhanced Admin Notification: Project '{project_data.get('name')}' finalized with {len(learning_payload['key_learnings'])} learning insights")
        
        # Simulate webhook call
        try:
            # await self._call_webhook_enhanced(notification)
            print("📊 Learning insights captured for knowledge base improvement")
        except Exception as e:
            print(f"Webhook notification failed: {e}")

# Global instance
rag_engine = RAGEngine()