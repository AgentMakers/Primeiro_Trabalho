# Agents WebSocket text capture

Este script conecta ao endpoint Agents Platform WebSocket e persiste apenas as transcrições/textos dos usuários em tempo real.

Propósito
- Capturar eventos `user_transcript` e `user_message` enviados pelo agente/serviço da ElevenLabs.
- Salvar imediatamente o texto e metadados mínimos em SQLite (`./data/whatsapp_storage.db`).
- Ignorar dados de áudio (não armazena áudios).

Arquivos principais
- `integrations/elevenlabs/clients/agents_ws_text_capture.py` — cliente executável que faz a conexão, reconecta com backoff e persiste eventos.

Dependências
- Python 3.8+
- pip install websockets

Variáveis de ambiente (PowerShell)

```powershell
$env:ELEVENLABS_API_KEY = 'sua_chave_aqui'
$env:AGENT_ID = 'seu_agent_id_aqui'
# opcional: caminho do DB (por padrão ./data/whatsapp_storage.db)
$env:WHATSAPP_DB_PATH = './data/whatsapp_storage.db'
```

Como executar (PowerShell)

```powershell
pip install websockets
python integrations/elevenlabs/clients/agents_ws_text_capture.py
```

O que é salvo
- session_id: conversation_id (quando disponível via `conversation_initiation_metadata`)
- user_id: se disponível no evento, caso contrário `eleven_user`
- text: transcrição do usuário
- timestamp: salvado pelo módulo de storage
- metadata: campo `raw_event` com o JSON do evento recebido

Boas práticas
- Não persista PII desnecessário; anonimize ou criptografe campos sensíveis antes do armazenamento.
- Para produção, use um banco gerenciado (Postgres) e filas (Redis) se precisar de throughput alto.
- Implemente monitoramento e retenção de dados.

Problemas comuns
- Falha na conexão: o script tenta reconectar com backoff exponencial.
- Chave inválida: verifique `ELEVENLABS_API_KEY` e permissões do agente.

Próximos passos sugeridos
- Adicionar um serviço supervisor (systemd/container) para manter o cliente rodando.
- Implementar deduplicação se a API reenviar mensagens em reconexões.
- Adicionar testes unitários para o storage (ex.: pytest para `sqlite_storage`).
