#backend/app/utils/chroma_db.py
import chromadb
from app.config.config import settings
from .ai_engine import get_jina_embeddings
import uuid

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

# Create collection
collection = chroma_client.get_or_create_collection(
    name="project_knowledge",
    metadata={"description": "Project scoping knowledge base"}
)

async def store_document(document: str, metadata: dict = None):
    """
    Store document in ChromaDB
    """
    try:
        # Get embeddings from Jina
        embeddings = await get_jina_embeddings(document)
        
        if embeddings:
            # Store with custom embeddings
            collection.add(
                embeddings=[embeddings],
                documents=[document],
                metadatas=[metadata] if metadata else [{}],
                ids=[str(uuid.uuid4())]
            )
        else:
            # Fallback: let ChromaDB generate embeddings
            collection.add(
                documents=[document],
                metadatas=[metadata] if metadata else [{}],
                ids=[str(uuid.uuid4())]
            )
            
        return True
    except Exception as e:
        print(f"Error storing document: {e}")
        return False

async def search_similar_projects(query: str, n_results: int = 3):
    """
    Search for similar projects
    """
    try:
        # Get query embeddings from Jina
        query_embedding = await get_jina_embeddings(query)
        
        if query_embedding:
            # Search with custom embeddings
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
        else:
            # Fallback: text-based search
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else []
        }
    except Exception as e:
        print(f"Error searching projects: {e}")
        return {"documents": [], "metadatas": [], "distances": []}

def get_collection_stats():
    """
    Get statistics about the knowledge base
    """
    try:
        collection_data = collection.get()
        return {
            "document_count": len(collection_data["ids"]),
            "collection_name": collection.name
        }
    except Exception as e:
        print(f"Error getting collection stats: {e}")
        return {"document_count": 0, "collection_name": "unknown"}