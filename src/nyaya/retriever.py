import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer

class LegalRetriever:
    """
    Retriever for legal documents using FAISS vector search.
    Now with IPC/BNS code filtering to prevent section confusion!
    """
    
    def __init__(self):
        # Load FAISS index and metadata
        index_path = os.getenv("FAISS_INDEX_PATH", "/Volumes/workspace_7474652263326815/default/nyaya_volumes/legal_index.faiss")
        metadata_path = os.getenv("FAISS_METADATA_PATH", "/Volumes/workspace_7474652263326815/default/nyaya_volumes/legal_metadata.pkl")
        
        try:
            self.index = faiss.read_index(index_path)
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            
            # Initialize embedding model (same as used for indexing)
            self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            
            print(f"✓ FAISS index loaded: {self.index.ntotal} documents")
            print(f"✓ Embedding model loaded: {self.embedding_model.get_sentence_embedding_dimension()}d")
            
        except FileNotFoundError as e:
            print(f"❌ FAISS index not found at {index_path}")
            print("Please run notebooks/02_build_faiss_index.py first!")
            raise
        except Exception as e:
            print(f"❌ Error loading FAISS index: {str(e)}")
            raise
    
    def _filter_by_code(self, results: list, code_filter: str) -> list:
        """
        Filter results by legal code (IPC or BNS).
        
        Args:
            results: List of retrieved documents
            code_filter: 'IPC', 'BNS', or 'BOTH'
            
        Returns:
            Filtered list of documents
        """
        if code_filter == 'BOTH':
            return results
        
        filtered = []
        for doc in results:
            # Extract code from source_ref (e.g., "IPC Section 302" or "BNS Section 103")
            source = doc.get('source', '')
            text = doc.get('text', '')
            
            # Check if document matches the requested code
            if code_filter == 'IPC':
                if 'IPC' in source or 'IPC Section' in text[:50]:
                    filtered.append(doc)
            elif code_filter == 'BNS':
                if 'BNS' in source or 'BNS Section' in text[:50] or 'Bharatiya Nyaya Sanhita' in text[:100]:
                    filtered.append(doc)
        
        return filtered if filtered else results  # Return all if no matches (fallback)
    
    def hybrid_search(self, query: str, top_k: int = 5, code_filter: str = 'BNS') -> list:
        """
        Semantic search with IPC/BNS code filtering.
        
        Args:
            query: The search query
            top_k: Number of results to return
            code_filter: 'IPC', 'BNS', or 'BOTH' (default: BNS)
            
        Returns:
            List of top-k relevant documents with metadata
        """
        # Input validation
        if not query or not query.strip():
            print("⚠️  Empty query provided")
            return []
        
        if top_k <= 0:
            print("⚠️  Invalid top_k value, using default: 5")
            top_k = 5
        
        try:
            # Generate embedding for query
            query_embedding = self.embedding_model.encode([query])[0].reshape(1, -1)
            
            # Retrieve more results than needed for filtering
            search_k = top_k * 3  # Get 3x results to filter from
            distances, indices = self.index.search(query_embedding, min(search_k, self.index.ntotal))
            
            # Build result list with metadata
            results = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx == -1:  # FAISS returns -1 for invalid indices
                    continue
                
                # Extract metadata
                text = self.metadata['texts'][idx] if idx < len(self.metadata['texts']) else ""
                source = self.metadata['sources'][idx] if idx < len(self.metadata['sources']) else ""
                doc_id = self.metadata['ids'][idx] if idx < len(self.metadata['ids']) else ""
                
                # Parse code and section from source or text
                code = 'UNKNOWN'
                section = 'N/A'
                if 'IPC Section' in text[:100]:
                    code = 'IPC'
                    import re
                    match = re.search(r'IPC Section (\d+[A-Z]?)', text[:100])
                    if match:
                        section = match.group(1)
                elif 'BNS Section' in text[:100] or 'Bharatiya Nyaya Sanhita' in text[:100]:
                    code = 'BNS'
                    import re
                    match = re.search(r'BNS Section (\d+[A-Z]?)|Section (\d+[A-Z]?)', text[:100])
                    if match:
                        section = match.group(1) or match.group(2)
                
                results.append({
                    'text': text,
                    'source': source,
                    'id': doc_id,
                    'code': code,
                    'section': section,
                    'score': float(distance)
                })
            
            # Apply code filtering
            filtered_results = self._filter_by_code(results, code_filter)
            
            # Return top-k after filtering
            final_results = filtered_results[:top_k]
            
            print(f"✓ Retrieved {len(final_results)} documents (filter: {code_filter})")
            return final_results
            
        except Exception as e:
            print(f"❌ Error during search: {str(e)}")
            return []

# Future migration path to Databricks Vector Search (managed service)
# 
# When ready to scale to production:
# 1. Create Vector Search endpoint: 
#    databricks vector-search create-endpoint --name legal-search
# 2. Create index from Unity Catalog table:
#    databricks vector-search create-index \
#      --name legal_vector_index \
#      --source-table workspace_7474652263326815.default.nyaya_unified_corpus \
#      --primary-key id \
#      --embedding-column text
# 3. Replace LegalRetriever with VectorSearchRetriever:
#    from databricks.vector_search.client import VectorSearchClient
#    client = VectorSearchClient()
#    results = client.search(index_name="legal_vector_index", query=query, num_results=5)
