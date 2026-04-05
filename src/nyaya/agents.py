from langgraph.graph import StateGraph, END
from langchain_databricks import ChatDatabricks
from .retriever import LegalRetriever

class AgentState(dict):
    pass

class LegalMultiAgent:
    def __init__(self):
        self.llm = ChatDatabricks(endpoint="databricks-llama-4-maverick")
        self.retriever = LegalRetriever()
        self.graph = self._build_graph()
    
    def _supervisor(self, state: AgentState):
        """Route and generate draft answer"""
        query = state["query"]
        
        # Retrieve context using hybrid search
        context_docs = self.retriever.hybrid_search(query, top_k=5)
        context_str = "\n\n".join([doc['text'] for doc in context_docs])
        
        # Generate draft answer
        prompt = f"""You are a legal assistant for Indian law (BNS, IPC). 
        Answer the question based only on the provided context.
        Question: {query}
        Context: {context_str}
        Answer:"""
        draft = self.llm.invoke(prompt).content
        return {"draft_answer": draft, "context_docs": context_docs}
    
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
        return {"final_answer": final}
    
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("supervisor", self._supervisor)
        workflow.add_node("auditor", self._auditor)
        workflow.set_entry_point("supervisor")
        workflow.add_edge("supervisor", "auditor")
        workflow.add_edge("auditor", END)
        return workflow.compile()
    
    def ask(self, query: str) -> str:
        result = self.graph.invoke({"query": query})
        return result.get("final_answer", "No answer generated.")