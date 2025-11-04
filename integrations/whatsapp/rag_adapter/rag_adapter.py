from typing import List, Dict, Any

class WhatsAppRAGAdapter:
    def __init__(self, rag_instance, default_top_k: int = 5, default_threshold: float = 0.3):
        self.rag = rag_instance
        self.default_top_k = default_top_k
        self.default_threshold = default_threshold

    def retrieve(self, query: str, top_k: int = None, score_threshold: float = None, session_context: Dict[str, Any] = None) -> List[Dict]:
        top_k = top_k or self.default_top_k
        score_threshold = score_threshold or self.default_threshold
        # Expect rag_instance to implement retrieve(...)
        return self.rag.retrieve(query=query, top_k=top_k, score_threshold=score_threshold, context=session_context)

    def format_for_whatsapp(self, docs: List[Dict]) -> str:
        # Convert docs into a concise WhatsApp-friendly text response
        parts = []
        for d in docs:
            parts.append(f"- {d.get('source','?')} ({d.get('score',0):.2%})")
            parts.append(d.get('text','')[:200])
        return "\n\n".join(parts)
