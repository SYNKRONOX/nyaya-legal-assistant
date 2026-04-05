from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_databricks import ChatDatabricks
from .retriever import LegalRetriever
from .sarvam_utils import SarvamAPI

# 1. The State now holds variables for both translation and legal drafting
class AgentState(TypedDict):
    query: str
    target_language: str
    english_query: str
    context_docs: list
    draft_answer: str
    final_english_answer: str
    final_indic_answer: str

class LegalMultiAgent:
    def __init__(self):
        # Initialize LLM, Retriever, AND Sarvam
        self.llm = ChatDatabricks(endpoint="databricks-llama-4-maverick")
        self.retriever = LegalRetriever()
        self.sarvam = SarvamAPI()
        self.graph = self._build_graph()
        
    # --- TRANSLATION IN ---
    def translate_in(self, state: AgentState):
        """Translates the user's native input into English for the Legal RAG."""
        target_lang = state.get('target_language', 'English')
        print(f"Translating input from {target_lang} to English...")
        
        eng_query = self.sarvam.translate(
            text=state['query'], 
            source_lang_name=target_lang, 
            target_lang_name="English"
        )
        return {"english_query": eng_query}

    # --- LEGAL BRAIN (SUPERVISOR) ---
    def _supervisor(self, state: AgentState):
        """Route and generate draft answer using the ENGLISH query"""
        # CRITICAL: We search using the translated english_query!
        query = state["english_query"]
        
        context_docs = self.retriever.hybrid_search(query, top_k=5)
        context_str = "\n\n".join([doc['text'] for doc in context_docs])
        
        prompt = f"""You are a legal assistant for Indian law (BNS, IPC). 
        Answer the question based only on the provided context.
        Question: {query}
        Context: {context_str}
        Answer:"""
        
        draft = self.llm.invoke(prompt).content
        return {"draft_answer": draft, "context_docs": context_docs}
    
    # --- LEGAL BRAIN (AUDITOR) ---
    def _auditor(self, state: AgentState):
        """Audit the answer for legal accuracy and fairness"""
        draft = state["draft_answer"]
        context = state["context_docs"]
        context_str = "\n".join([doc['text'][:500] for doc in context])
        
        audit_prompt = f"""Review this legal answer. If it is accurate and fair, return it unchanged.
        If there are errors or missing citations, correct it.
        
        Context: {context_str}
        Draft answer: {draft}
        
        Final answer (with citations if possible):"""
        
        final = self.llm.invoke(audit_prompt).content
        # Save to final_english_answer so the translator can catch it
        return {"final_english_answer": final}

    # --- TRANSLATION OUT ---
    def translate_out(self, state: AgentState):
        """Translates the English legal answer back to the user's native language."""
        target_lang = state.get('target_language', 'English')
        print(f"Translating answer to {target_lang}...")
        
        indic_answer = self.sarvam.translate(
            text=state['final_english_answer'], 
            source_lang_name="English", 
            target_lang_name=target_lang
        )
        return {"final_indic_answer": indic_answer}

    # --- BUILD THE GRAPH ---
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("translator_in", self.translate_in)
        workflow.add_node("supervisor", self._supervisor)
        workflow.add_node("auditor", self._auditor)
        workflow.add_node("translator_out", self.translate_out)
        
        # Connect the 4-stage pipeline
        workflow.set_entry_point("translator_in")
        workflow.add_edge("translator_in", "supervisor")
        workflow.add_edge("supervisor", "auditor")
        workflow.add_edge("auditor", "translator_out")
        workflow.add_edge("translator_out", END)
        
        return workflow.compile()
    
    # --- EXECUTE ---
    def ask(self, query: str, target_language: str = "English") -> str:
        """Kicks off the pipeline with the user's chosen language."""
        result = self.graph.invoke({
            "query": query, 
            "target_language": target_language
        })
        return result.get("final_indic_answer", "No answer generated.")