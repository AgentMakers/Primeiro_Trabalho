from typing import List, Dict, Any

class ElevenLabsRAGAdapter:
    def __init__(self, rag_instance, default_top_k: int = 5, default_threshold: float = 0.3):
        self.rag = rag_instance
        self.default_top_k = default_top_k
        self.default_threshold = default_threshold

    def retrieve_for_call(self, session_id: str, query: str, top_k: int = None, score_threshold: float = None) -> List[Dict]:
        top_k = top_k or self.default_top_k
        score_threshold = score_threshold or self.default_threshold
        # session_id may be used to fetch session history/context
        return self.rag.retrieve(query=query, top_k=top_k, score_threshold=score_threshold, context={"session_id": session_id})

    def summarize_for_tts(self, docs: List[Dict], max_chars: int = 1000) -> str:
        # Produce concise text suitable for TTS
        text = "\n\n".join(d.get("text","") for d in docs)
        return text[:max_chars]
