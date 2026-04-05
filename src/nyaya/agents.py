from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_databricks import ChatDatabricks
from .retriever import LegalRetriever
import mlflow
import time
import re

# State holds variables for translation and legal processing
class AgentState(TypedDict):
    query: str
    target_language: str
    detected_code: str  # IPC, BNS, or BOTH
    user_intent: str  # "current_law", "historical", "comparison", "law_student"
    context_docs: list
    final_answer: str
    error: str

class LegalMultiAgent:
    def __init__(self):
        # Initialize LLM and Retriever (no external translation API!)
        self.llm = ChatDatabricks(endpoint="databricks-llama-4-maverick")
        self.retriever = LegalRetriever()
        self.graph = self._build_graph()
        print("✓ Legal Multi-Agent initialized successfully (with IPC/BNS disambiguation)")
        print("✓ CRITICAL: IPC repealed July 1, 2024 → BNS is now the law of the land!")
        
    def _detect_user_intent(self, query: str) -> str:
        """
        Detect user intent to determine whether to show IPC information.
        
        CRITICAL: As of July 1, 2024, IPC was repealed. BNS is current law.
        
        Returns:
            - "current_law": User asking about current law (BNS only)
            - "historical": User asking about IPC specifically (historical/educational)
            - "comparison": User wants to compare IPC vs BNS (law student use case)
            - "law_student": Educational query (show both for learning)
        """
        query_lower = query.lower()
        
        # Explicit IPC request (historical/educational)
        if re.search(r'\bipc\b', query_lower):
            return "historical"
        
        # Comparison/educational queries
        comparison_keywords = ['difference', 'compare', 'vs', 'versus', 'changed', 
                              'old vs new', 'before and after', 'replaced']
        if any(kw in query_lower for kw in comparison_keywords):
            return "comparison"
        
        # Law student indicators
        law_student_keywords = ['study', 'learn', 'understand', 'explain both', 
                               'history', 'evolution', 'transition']
        if any(kw in query_lower for kw in law_student_keywords):
            return "law_student"
        
        # Default: Current law (BNS only)
        return "current_law"
    
    def _detect_legal_code(self, query: str, user_intent: str) -> str:
        """
        Detect which legal code to retrieve based on user intent.
        
        PRIORITY: BNS (current law) unless explicitly requesting IPC
        
        Returns: 'IPC', 'BNS', or 'BOTH'
        """
        query_lower = query.lower()
        
        # Explicit code mentions
        has_ipc = bool(re.search(r'\bipc\b', query_lower))
        has_bns = bool(re.search(r'\b(bns|bharatiya nyaya sanhita|nyaya sanhita)\b', query_lower))
        
        # Intent-based logic
        if user_intent == "current_law":
            # Only BNS (IPC is repealed)
            return 'BNS'
        elif user_intent == "historical":
            # User explicitly asked about IPC
            return 'IPC'
        elif user_intent in ["comparison", "law_student"]:
            # Educational: show both codes
            return 'BOTH'
        
        # Fallback: Check explicit mentions
        if has_ipc and has_bns:
            return 'BOTH'
        elif has_ipc:
            return 'IPC'
        elif has_bns:
            return 'BNS'
        else:
            # DEFAULT: BNS (current law)
            return 'BNS'
    
    def _should_skip_processing(self, state: AgentState) -> bool:
        """Check if we should skip to END due to empty query"""
        return not state.get('query', '').strip()
    
    def _legal_rag_pipeline(self, state: AgentState):
        """
        Combined RAG pipeline with IPC/BNS disambiguation and legal context awareness.
        
        CRITICAL: IPC repealed July 1, 2024. BNS is current law.
        """
        query = state['query']
        target_lang = state.get('target_language', 'English')
        
        try:
            # Step 1: Detect user intent (what are they really asking?)
            user_intent = self._detect_user_intent(query)
            
            # Step 2: Detect which legal code to retrieve
            detected_code = self._detect_legal_code(query, user_intent)
            
            # Step 3: Retrieve context documents with code filtering
            context_docs = self.retriever.hybrid_search(
                query, 
                k=5,
                code_filter=detected_code
            )
            
            if not context_docs:
                fallback_msg = {
                    "current_law": "I couldn't find relevant information in the BNS database. Please try rephrasing your question.",
                    "historical": "I couldn't find relevant IPC information. Note: IPC was repealed on July 1, 2024 and replaced by BNS.",
                    "comparison": "I couldn't find relevant information for comparison. Please be more specific.",
                    "law_student": "I couldn't find relevant information. Please try rephrasing your question."
                }.get(user_intent, "I couldn't find relevant information.")
                
                return {
                    "context_docs": [],
                    "detected_code": detected_code,
                    "user_intent": user_intent,
                    "final_answer": fallback_msg,
                    "error": ""
                }
            
            # Step 4: Build context string from actual document structure
            context_str = "\n\n".join([
                f"[Document {i+1}] {doc.get('text', '')[:500]}" 
                for i, doc in enumerate(context_docs)
            ])
            
            # Step 5: Build prompt based on user intent
            prompts = {
                "current_law": self._build_current_law_prompt(query, context_str, target_lang),
                "historical": self._build_historical_prompt(query, context_str, target_lang),
                "comparison": self._build_comparison_prompt(query, context_str, target_lang),
                "law_student": self._build_educational_prompt(query, context_str, target_lang)
            }
            
            prompt = prompts.get(user_intent, prompts["current_law"])
            
            # Step 6: Single LLM call
            answer = self.llm.invoke(prompt).content
            
            return {
                "context_docs": context_docs,
                "detected_code": detected_code,
                "user_intent": user_intent,
                "final_answer": answer,
                "error": ""
            }
            
        except Exception as e:
            error_msg = f"Error in RAG pipeline: {str(e)}"
            print(error_msg)
            return {
                "context_docs": [],
                "detected_code": "UNKNOWN",
                "user_intent": "current_law",
                "final_answer": f"An error occurred while processing your question. Please try again. ({type(e).__name__})",
                "error": error_msg
            }
    
    def _build_current_law_prompt(self, query: str, context: str, lang: str) -> str:
        """Prompt for general public asking about current law (BNS only)"""
        base = f"""You are a legal assistant specializing in Indian criminal law.

CRITICAL LEGAL CONTEXT:
- As of July 1, 2024, the Indian Penal Code (IPC 1860) was REPEALED
- Bharatiya Nyaya Sanhita (BNS 2023) is now the CURRENT LAW of India
- All your answers MUST cite BNS (not IPC) unless the user explicitly asks about IPC

Question: {query}

Legal Context (BNS):
{context}

Instructions:
1. Answer based ONLY on the provided BNS context
2. Format citations as: "BNS Section XXX"
3. Do NOT mention IPC (it's repealed and no longer applicable)
4. Be clear this is the CURRENT law in India
5. Be concise and accurate"""

        if lang != "English":
            base += f"\n6. Provide your answer in {lang} language\n\nAnswer in {lang}:"
        else:
            base += "\n\nAnswer:"
        
        return base
    
    def _build_historical_prompt(self, query: str, context: str, lang: str) -> str:
        """Prompt for queries explicitly about IPC (historical/educational)"""
        base = f"""You are a legal assistant specializing in Indian criminal law history.

CRITICAL LEGAL CONTEXT:
- The user is asking about the Indian Penal Code (IPC 1860)
- IPC was REPEALED on July 1, 2024 and replaced by BNS
- This is for HISTORICAL or EDUCATIONAL purposes only

Question: {query}

Legal Context (IPC):
{context}

Instructions:
1. Answer based on the provided IPC context
2. Format citations as: "IPC Section XXX"
3. ALWAYS mention: "Note: IPC was repealed July 1, 2024. For current law, see BNS."
4. Be clear this is HISTORICAL information
5. Be concise and accurate"""

        if lang != "English":
            base += f"\n6. Provide your answer in {lang} language\n\nAnswer in {lang}:"
        else:
            base += "\n\nAnswer:"
        
        return base
    
    def _build_comparison_prompt(self, query: str, context: str, lang: str) -> str:
        """Prompt for comparison queries (IPC vs BNS)"""
        base = f"""You are a legal assistant specializing in Indian criminal law transitions.

CRITICAL LEGAL CONTEXT:
- IPC (1860-2024): Old law, now REPEALED
- BNS (2023-present): New law, CURRENTLY APPLICABLE
- User wants to understand the changes/differences

Question: {query}

Legal Context (IPC and BNS):
{context}

Instructions:
1. Compare BOTH IPC and BNS provisions
2. Format: "IPC Section XXX (repealed) vs BNS Section YYY (current)"
3. Highlight key changes and differences
4. Make clear which is historical (IPC) and which is current (BNS)
5. Explain practical implications of the changes
6. Be concise and clear"""

        if lang != "English":
            base += f"\n7. Provide your answer in {lang} language\n\nAnswer in {lang}:"
        else:
            base += "\n\nAnswer:"
        
        return base
    
    def _build_educational_prompt(self, query: str, context: str, lang: str) -> str:
        """Prompt for law students (educational focus)"""
        base = f"""You are a legal educator specializing in Indian criminal law.

CRITICAL LEGAL CONTEXT:
- Student is learning about Indian criminal law
- IPC (1860-2024): Historical law, repealed July 1, 2024
- BNS (2023-present): Current law, replaced IPC
- Educational value in understanding both

Question: {query}

Legal Context (IPC and BNS):
{context}

Instructions:
1. Provide educational answer covering both IPC and BNS
2. Format: Start with BNS (current law), then explain IPC (historical)
3. Example: "Under current law (BNS Section XXX)... Previously under IPC Section YYY..."
4. Explain WHY the law changed (if relevant)
5. Help student understand the evolution
6. Be clear about which is current vs historical
7. Be concise but educational"""

        if lang != "English":
            base += f"\n8. Provide your answer in {lang} language\n\nAnswer in {lang}:"
        else:
            base += "\n\nAnswer:"
        
        return base
    
    def _build_graph(self):
        """Build a simplified graph with single RAG node"""
        workflow = StateGraph(AgentState)
        
        # Single node for the entire RAG pipeline
        workflow.add_node("legal_rag", self._legal_rag_pipeline)
        
        # Simple linear flow
        workflow.set_entry_point("legal_rag")
        workflow.add_edge("legal_rag", END)
        
        return workflow.compile()
    
    def ask(self, query: str, target_language: str = "English") -> str:
        """
        Process a legal query with optional multilingual output and IPC/BNS disambiguation
        
        CRITICAL: As of July 1, 2024, IPC is REPEALED. BNS is current law.
        
        Args:
            query: The legal question
            target_language: Target language for the response (default: English)
            
        Returns:
            The legal answer in the requested language
        """
        # Input validation
        if not query or not query.strip():
            return "Please enter a legal question."
        
        if len(query) > 2000:
            return "Query is too long. Please limit to 2000 characters."
        
        # MLflow tracking
        with mlflow.start_run(run_name=f"legal_query_{target_language}"):
            try:
                # Log parameters
                mlflow.log_param("target_language", target_language)
                mlflow.log_param("query_length", len(query))
                mlflow.log_param("query_preview", query[:100])
                
                # Execute graph
                start_time = time.time()
                result = self.graph.invoke({
                    "query": query,
                    "target_language": target_language
                })
                latency = time.time() - start_time
                
                # Log metrics including detected code and user intent
                mlflow.log_metric("latency_seconds", latency)
                mlflow.log_metric("num_context_docs", len(result.get("context_docs", [])))
                mlflow.log_metric("answer_length", len(result.get("final_answer", "")))
                mlflow.log_param("detected_code", result.get("detected_code", "UNKNOWN"))
                mlflow.log_param("user_intent", result.get("user_intent", "current_law"))
                
                if result.get("error"):
                    mlflow.log_param("error", result["error"])
                
                # Log success
                mlflow.log_param("status", "success" if not result.get("error") else "error")
                
                return result.get("final_answer", "No answer generated.")
                
            except Exception as e:
                # Log failure
                error_msg = f"{type(e).__name__}: {str(e)}"
                mlflow.log_param("status", "failure")
                mlflow.log_param("error", error_msg)
                print(f"Error in ask(): {error_msg}")
                return f"An unexpected error occurred. Please try again later. ({type(e).__name__})"
