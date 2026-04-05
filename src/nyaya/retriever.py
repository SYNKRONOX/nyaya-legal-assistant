from databricks import sql as db_sql
import os
from .faiss_utils import FAISSRetriever

class LegalRetriever:
    def __init__(self):
        self.retriever = FAISSRetriever()
        # Ensure DATABRICKS_HOST, DATABRICKS_TOKEN, and DATABRICKS_SQL_WAREHOUSE_ID are in App Environment Variables
        self.warehouse_id = os.environ.get("DATABRICKS_SQL_WAREHOUSE_ID")
    
    def vector_search(self, query, top_k=5):
        return self.retriever.search(query, top_k)
    
    def keyword_search(self, query, top_k=5):
        escaped_query = query.replace("'", "''") 
        
        # Note: Pointing to your specific workspace catalog
        sql_query = f"""
            SELECT text, source,
                   (LENGTH(text) - LENGTH(REPLACE(LOWER(text), LOWER('{escaped_query}'), ''))) / LENGTH('{escaped_query}') AS score
            FROM workspace_7474652263326815.default.nyaya_legal_corpus
            WHERE LOWER(text) LIKE CONCAT('%', LOWER('{escaped_query}'), '%')
            ORDER BY score DESC
            LIMIT {top_k}
        """
        
        with db_sql.connect(
            server_hostname=os.environ.get("DATABRICKS_HOST"),
            http_path=f"/sql/1.0/warehouses/{self.warehouse_id}",
            access_token=os.environ.get("DATABRICKS_TOKEN")
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                rows = cursor.fetchall()
                
        results = []
        for row in rows:
            results.append({
                'text': row.text,
                'source': row.source,
                'score': float(row.score)
            })
        return results
    
    def hybrid_search(self, query, top_k=5, vector_weight=0.7, keyword_weight=0.3):
        vector_results = self.vector_search(query, top_k=top_k*2)
        keyword_results = self.keyword_search(query, top_k=top_k*2)
        
        # Reciprocal Rank Fusion (RRF)
        scores = {}
        for rank, res in enumerate(vector_results):
            doc_id = res['text']  
            scores[doc_id] = scores.get(doc_id, 0) + vector_weight / (rank + 1)
        for rank, res in enumerate(keyword_results):
            doc_id = res['text']
            scores[doc_id] = scores.get(doc_id, 0) + keyword_weight / (rank + 1)
        
        # Sort by score and return top_k
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        final_results = []
        for doc_text, score in sorted_docs:
            for res in vector_results + keyword_results:
                if res['text'] == doc_text:
                    final_results.append(res)
                    break
        return final_results