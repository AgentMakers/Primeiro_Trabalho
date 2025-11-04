# integrations

Este diretório contém integrações com canais externos (WhatsApp, ElevenLabs).

Estrutura:
- whatsapp/: Conector, handlers, adapters e assets para bot via WhatsApp.
- elevenlabs/: TTS/STT, telephony e adapters para chamadas de voz.
- shared/: utilitários e infra compartilhados.

Contrato do rag_adapter:
- Deve expor retrieve(query, top_k, score_threshold, context)
- Deve devolver lista de documentos com keys: text, source, score, category

Uso:
- Preencha `.env` com as chaves necessárias.
- Importe adapters via: `from integrations.whatsapp.rag_adapter.rag_adapter import WhatsAppRAGAdapter`
