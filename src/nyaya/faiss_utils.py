import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer
import os
import shutil

class FAISSRetriever:
    def __init__(self):
        # Read from environment variables set in app.yaml
        self.index_file = os.environ.get("FAISS_INDEX_PATH", "/Volumes/workspace_7474652263326815/default/nyaya_volumes/legal_index.faiss")
        self.metadata_file = os.environ.get("FAISS_METADATA_PATH", "/Volumes/workspace_7474652263326815/default/nyaya_volumes/legal_metadata.pkl")
        
        # --- BULLETPROOF FUSE FIX ---
        local_index = "/tmp/local_index.faiss"
        local_meta = "/tmp/local_metadata.pkl"
        
        # Copy files to local container memory first to avoid C++ network read errors
        if not os.path.exists(local_index):
            print("Copying index files from Unity Catalog to local container...")
            shutil.copyfile(self.index_file, local_index)
            shutil.copyfile(self.metadata_file, local_meta)
        
        # Load index and metadata from the local /tmp/ copies
        self.index = faiss.read_index(local_index)
        with open(local_meta, 'rb') as f:
            self.metadata = pickle.load(f)
        # ----------------------------
        
        # Load embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print(f"Loaded FAISS index with {self.index.ntotal} vectors")
    
    def search(self, query, top_k=5):
        # Encode query
        query_emb = self.model.encode([query])[0].astype(np.float32)
        query_emb = np.expand_dims(query_emb, axis=0)
        faiss.normalize_L2(query_emb)
        
        # Search
        distances, indices = self.index.search(query_emb, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            results.append({
                'text': self.metadata['texts'][idx],
                'source': self.metadata['sources'][idx],
                'score': float(distances[0][i])
            })
        return results