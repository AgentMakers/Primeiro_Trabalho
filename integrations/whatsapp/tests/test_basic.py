import pytest
from integrations.whatsapp.rag_adapter.rag_adapter import WhatsAppRAGAdapter

class DummyRAG:
    def retrieve(self, query, top_k, score_threshold, context=None):
        return [{"text":"doc1","source":"file1","score":0.9}]

def test_whatsapp_adapter_retrieve():
    adapter = WhatsAppRAGAdapter(DummyRAG())
    docs = adapter.retrieve("teste")
    assert isinstance(docs, list)
    assert docs[0]["score"] > 0
