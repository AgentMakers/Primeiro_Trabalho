# integrations/whatsapp/storage

Responsabilidade:
- Logs e metadata de conversas (por usuário, por sessão).
- Persistência mínima: last_seen, context, message history.

Opções:
- SQLite local, arquivos JSON, ou serviço externo (Redis/Postgres).

TODO:
- Schemas e exemplo local (SQLite).
