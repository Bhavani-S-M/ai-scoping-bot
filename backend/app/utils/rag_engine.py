# backend/app/utils/rag_engine.py
import chromadb
from app.config.config import settings
from .ai_engine import get_jina_embeddings
import uuid
import json
import os
from typing import List, Dict, Any


class RAGEngine:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection(
            name="project_knowledge",
            metadata={"description": "Project scoping knowledge base"}
        )
        self.knowledge_base_path = "knowledge_base/docs"
    
    async def initialize_knowledge_base(self):
        """Load knowledge base documents on startup"""
        try:
            if not os.path.exists(self.knowledge_base_path):
                print(f"⚠️ Knowledge base path not found: {self.knowledge_base_path}")
                print(f"📁 Creating directory: {self.knowledge_base_path}")
                os.makedirs(self.knowledge_base_path, exist_ok=True)
                return
            
            # Check if already initialized
            count = self.collection.count()
            if count > 0:
                print(f"✅ Knowledge base already initialized with {count} documents")
                return
            
            print("📚 Initializing knowledge base...")
            loaded = 0
            
            for root, dirs, files in os.walk(self.knowledge_base_path):
                for file in files:
                    if file.endswith(('.txt', '.md', '.json')):
                        file_path = os.path.join(root, file)
                        await self._load_knowledge_file(file_path)
                        loaded += 1
            
            if loaded == 0:
                print(f"⚠️ No knowledge base files found in {self.knowledge_base_path}")
                print("💡 Add .txt, .md, or .json files to populate the knowledge base")
            else:
                print(f"✅ Loaded {loaded} knowledge base documents")
        except Exception as e:
            print(f"❌ Error initializing knowledge base: {e}")
    
    async def _load_knowledge_file(self, file_path: str):
        """Load a single knowledge base file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata from filename
            filename = os.path.basename(file_path)
            domain = filename.split('_')[0] if '_' in filename else 'general'
            
            metadata = {
                "source": filename,
                "domain": domain,
                "type": "knowledge_base",
                "file_path": file_path
            }
            
            # Get embeddings and store
            embeddings = await get_jina_embeddings(content)
            
            if embeddings:
                self.collection.add(
                    embeddings=[embeddings],
                    documents=[content],
                    metadatas=[metadata],
                    ids=[str(uuid.uuid4())]
                )
            else:
                self.collection.add(
                    documents=[content],
                    metadatas=[metadata],
                    ids=[str(uuid.uuid4())]
                )
            print(f"  ✓ Loaded: {filename}")
        except Exception as e:
            print(f"  ✗ Error loading {file_path}: {e}")
    
    async def store_project_scope(self, project_data: Dict[str, Any], scope_data: Dict[str, Any]):
        """Store completed project scope in knowledge base"""
        try:
            doc_text = self._create_document_text(project_data, scope_data)
            embeddings = await get_jina_embeddings(doc_text)
            
            metadata = {
                "project_id": str(project_data.get('id', '')),
                "project_name": project_data.get('name', ''),
                "domain": project_data.get('domain', ''),
                "complexity": project_data.get('complexity', ''),
                "tech_stack": project_data.get('tech_stack', ''),
                "total_cost": scope_data.get('cost_breakdown', {}).get('total_cost', 0),
                "duration": scope_data.get('timeline', {}).get('total_duration_months', 0),
                "type": "project_scope"
            }
            
            if embeddings:
                self.collection.add(
                    embeddings=[embeddings],
                    documents=[doc_text],
                    metadatas=[metadata],
                    ids=[str(uuid.uuid4())]
                )
            else:
                self.collection.add(
                    documents=[doc_text],
                    metadatas=[metadata],
                    ids=[str(uuid.uuid4())]
                )
            
            return True
        except Exception as e:
            print(f"Error storing project scope: {e}")
            return False
    
    async def search_similar_projects(self, query: str, filters: Dict[str, Any] = None, n_results: int = 5):
        """Search for similar projects with optional filters"""
        try:
            query_embedding = await get_jina_embeddings(query)
            
            where_clause = {}
            if filters:
                where_clause = {k: v for k, v in filters.items() if v is not None}
            
            if query_embedding:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=where_clause if where_clause else None
                )
            else:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=where_clause if where_clause else None
                )
            
            return self._process_search_results(results)
        except Exception as e:
            print(f"Error searching projects: {e}")
            return {"documents": [], "metadatas": [], "distances": [], "similar_projects": []}
    
    def _create_document_text(self, project_data: Dict[str, Any], scope_data: Dict[str, Any]) -> str:
        """Create searchable text from project and scope data"""
        text_parts = [
            f"Project: {project_data.get('name', '')}",
            f"Domain: {project_data.get('domain', '')}",
            f"Complexity: {project_data.get('complexity', '')}",
            f"Tech Stack: {project_data.get('tech_stack', '')}",
            f"Use Cases: {project_data.get('use_cases', '')}",
        ]
        
        overview = scope_data.get('overview', {})
        text_parts.append(f"Summary: {overview.get('project_summary', '')}")
        text_parts.extend([f"Objective: {obj}" for obj in overview.get('key_objectives', [])])
        
        activities = scope_data.get('activities', [])
        for activity in activities[:10]:
            text_parts.append(f"Activity: {activity.get('name', '')} - {activity.get('phase', '')}")
        
        resources = scope_data.get('resources', [])
        for resource in resources:
            text_parts.append(f"Role: {resource.get('role', '')} - {resource.get('effort_months', 0)} months")
        
        return "\n".join(text_parts)
    
    def _process_search_results(self, results: Dict) -> Dict:
        """Process and enhance search results"""
        similar_projects = []
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results.get('documents', [[]])[0],
            results.get('metadatas', [[]])[0],
            results.get('distances', [[]])[0]
        )):
            similar_projects.append({
                "id": i,
                "similarity_score": 1 - distance,
                "project_name": metadata.get('project_name', metadata.get('source', 'Unknown')),
                "domain": metadata.get('domain', ''),
                "complexity": metadata.get('complexity', ''),
                "total_cost": metadata.get('total_cost', 0),
                "duration": metadata.get('duration', 0),
                "key_insights": self._extract_insights_from_doc(doc)
            })
        
        return {
            "documents": results.get('documents', [[]])[0],
            "metadatas": results.get('metadatas', [[]])[0],
            "distances": results.get('distances', [[]])[0],
            "similar_projects": similar_projects
        }
    
    def _extract_insights_from_doc(self, doc: str) -> List[str]:
        """Extract key insights from document text"""
        insights = []
        lines = doc.split('\n')
        
        for line in lines[:5]:
            if any(keyword in line.lower() for keyword in ['activity:', 'role:', 'objective:', 'phase']):
                insights.append(line.strip())
        
        return insights[:3]


# Global RAG engine instance
rag_engine = RAGEngine()