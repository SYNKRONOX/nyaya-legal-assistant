import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from .download_util import download_volume_files

class LegalRetriever:
    def __init__(self):
        print("🔍 Initializing Legal Retriever...")
        
        # Download files from volume at startup
        try:
            data_dir = download_volume_files()
            index_path = os.path.join(data_dir, "legal_index.faiss")
            metadata_path = os.path.join(data_dir, "legal_metadata.pkl")
        except Exception as e:
            print(f"❌ Failed to download files from volume: {e}")
            print("   Falling back to local paths (for development)")
            # Fallback for local development
            source_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_dir = os.path.join(source_root, "data")
            index_path = os.path.join(data_dir, "legal_index.faiss")
            metadata_path = os.path.join(data_dir, "legal_metadata.pkl")
        
        print(f"📂 Loading FAISS index from: {index_path}")
        print(f"📂 Loading metadata from: {metadata_path}")
        
        # Check if files exist
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index not found at: {index_path}")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata not found at: {metadata_path}")
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            print(f"✅ Loaded FAISS index with {self.index.ntotal} vectors")
            
            # Load metadata (dict with keys: texts, sources, ids)
            with open(metadata_path, 'rb') as f:
                metadata_dict = pickle.load(f)
            
            # Extract lists
            self.texts = metadata_dict.get('texts', [])
            self.sources = metadata_dict.get('sources', [])
            self.ids = metadata_dict.get('ids', [])
            
            print(f"✅ Loaded {len(self.texts)} text records")
            print(f"✅ Loaded {len(self.sources)} source records")
            
            # Load embedding model
            self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            print("✅ Loaded embedding model")
            
        except Exception as e:
            print(f"❌ Error loading FAISS index: {e}")
            raise
    
    def _detect_code_from_text(self, text):
        """Detect if text is about IPC or BNS based on content"""
        text_lower = text.lower()
        
        # Check for explicit mentions
        if 'ipc' in text_lower or 'indian penal code' in text_lower:
            return 'IPC'
        if 'bns' in text_lower or 'bharatiya nyaya sanhita' in text_lower:
            return 'BNS'
        
        # Check for section patterns
        if 'section' in text_lower:
            # Could be either, return as general legal
            return 'GENERAL'
        
        return 'GENERAL'
    
    def _filter_by_code(self, results, code_filter):
        """Filter search results by legal code (IPC/BNS/BOTH)"""
        if code_filter == 'BOTH':
            return results
        
        filtered = []
        for doc in results:
            text = doc.get('text', '')
            doc_code = self._detect_code_from_text(text)
            
            # If looking for specific code, match it or accept GENERAL
            if code_filter == doc_code or doc_code == 'GENERAL':
                filtered.append(doc)
        
        return filtered
    
    def hybrid_search(self, query, k=5, code_filter='BOTH'):
        """
        Perform hybrid search with optional code filtering
        
        Args:
            query: Search query
            k: Number of results to return
            code_filter: 'IPC', 'BNS', or 'BOTH'
        """
        try:
            # Embed query
            query_vector = self.embedding_model.encode([query])
            
            # Search FAISS (get more results for filtering)
            search_k = min(k * 3, len(self.texts))
            distances, indices = self.index.search(query_vector, search_k)
            
            # Gather results
            results = []
            for idx in indices[0]:
                if idx >= 0 and idx < len(self.texts):
                    # Build document dict from parallel lists
                    doc = {
                        'text': self.texts[idx],
                        'source': self.sources[idx] if idx < len(self.sources) else 'Unknown',
                        'id': self.ids[idx] if idx < len(self.ids) else str(idx),
                        'index': idx
                    }
                    results.append(doc)
            
            # Filter by code if needed
            if code_filter != 'BOTH':
                results = self._filter_by_code(results, code_filter)
            
            # Return top k
            return results[:k]
            
        except Exception as e:
            print(f"❌ Error in hybrid_search: {e}")
            import traceback
            traceback.print_exc()
            return []
