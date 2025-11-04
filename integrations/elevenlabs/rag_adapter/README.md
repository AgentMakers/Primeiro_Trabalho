# integrations/elevenlabs/rag_adapter

Responsabilidade:
- Adaptador que usa RAG para gerar contexto/respostas em chamadas de voz.
- Estratégias para reduzir latência e tamanho do prompt em voz.

Interface sugerida:
- retrieve_for_call(session_id, query, top_k=5, score_threshold=0.3)

TODO:
- Política de resumo entre turns.
