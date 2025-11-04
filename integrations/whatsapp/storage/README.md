# integrations/whatsapp/storage

Responsabilidade:
- Logs e metadata de conversas (por usuário, por sessão).
- Persistência mínima: last_seen, context, message history.

Opções:
- SQLite local, arquivos JSON, ou serviço externo (Redis/Postgres).

TODO:
- Schemas e exemplo local (SQLite).


## Esquema proposto (SQLite)

Campos principais da tabela `user_questions`:
- id (TEXT PRIMARY KEY) — uuid
- user_id (TEXT) — identificador do usuário / número
- session_id (TEXT) — id da sessão/conversa
- channel (TEXT) — ex: "whatsapp"
- text (TEXT) — texto original recebido
- normalized_text (TEXT) — versão normalizada (opcional)
- timestamp (TEXT) — ISO8601 UTC
- embedding_id (TEXT) — id do embedding no vector DB (opcional)
- rag_result_id (TEXT) — id da resposta RAG (opcional)
- tts_generated (INTEGER) — 0/1
- audio_uri (TEXT) — caminho ou URL do áudio gerado (opcional)
- metadata (JSON) — informações extras (intent, confidence, language, alignment, etc.)


## Exemplo de uso (SQLite)

- Módulo de referência: `integrations.whatsapp.storage.sqlite_storage`

Fluxo recomendado:
1. No webhook/handler que recebe a mensagem do usuário, chame `save_question()` imediatamente para persistir o texto original.
2. Gere embedding e armazene o `embedding_id` com `set_embedding_id()` (opcional).
3. Execute a busca RAG; armazene o resultado com `set_rag_result()`.
4. Se gerar TTS via ElevenLabs, salve o `audio_uri` com `set_tts_info()`.


## Exemplo rápido (Python)

```py
from integrations.whatsapp.storage import sqlite_storage as storage

DB = "./data/whatsapp_storage.db"
storage.init_db(DB)
qid = storage.save_question(DB, user_id="user-123", session_id="sess-1", channel="whatsapp", text="Olá, preciso de ajuda")
# ... gerar embedding ...
# storage.set_embedding_id(DB, qid, embedding_id)
# ... RAG ...
# storage.set_rag_result(DB, qid, rag_id)
# ... TTS ...
# storage.set_tts_info(DB, qid, "/tmp/audio123.mp3")
```


## Notas
- Para produção, prefira um banco gerenciado (Postgres) e trate PII adequadamente.
- Considere criptografar campos sensíveis e aplicar política de retenção.
