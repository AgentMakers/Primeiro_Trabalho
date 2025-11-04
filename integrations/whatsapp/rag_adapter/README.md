# integrations/whatsapp/rag_adapter

Responsabilidade:
- Adaptador que consome o RAG para consultas originadas por conversas WhatsApp.
- Enriquecer contexto, formatar respostas, aplicar top_k/threshold.

Interface sugerida:
- init(config)
- retrieve(query, top_k=5, score_threshold=0.3, context=None)
- format_for_whatsapp(document_list)

TODO:
- Implementar cache de contexto por sessão.
