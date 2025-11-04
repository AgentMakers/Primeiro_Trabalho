# ElevenLabs WebSocket text capture (multi-stream)

Este diretório contém um cliente de exemplo que conecta ao endpoint *multi-stream* da ElevenLabs e persiste apenas textos (não salva áudios).

Requisitos
- Python 3.8+
- pip install websockets

Variáveis de ambiente (PowerShell):

```powershell
$env:ELEVENLABS_API_KEY = 'sua_chave'
$env:VOICE_ID = 'seu_voice_id'
$env:WHATSAPP_DB_PATH = './data/whatsapp_messages.jsonl'  # opcional
```

Executar o cliente (exemplo):

```powershell
python integrations/elevenlabs/clients/tts_multi_ws_text_capture.py
```

Observações
- O cliente lê linhas do stdin e envia como mensagens de texto (`sendText`).
- Apenas mensagens textuais (saindo ou vindas do servidor) são salvas com o `json_storage` (JSONL) por padrão.
- Para persistência em SQLite, use o módulo `integrations.whatsapp.storage.sqlite_storage` diretamente (já está disponível no repositório).

Endpoint Flask
- Há um endpoint simples em `app/webhook_elevenlabs.py` que recebe POSTs JSON com `{ "text": "...", "user": "id", "session": "s1" }` e salva apenas o texto.
- Exemplo curl abaixo.

Exemplo curl:

```bash
curl -X POST http://localhost:8001/webhook/elevenlabs -H "Content-Type: application/json" -d '{"text":"Olá, isto é um teste","user":"user-1","session":"sess-1"}'
```

Segurança
- Nunca coloque chaves em repositório. Use variáveis de ambiente.
- Este código é para prototipagem; ajuste validações e limites para produção.
