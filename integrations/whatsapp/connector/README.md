# integrations/whatsapp/connector

Responsabilidade:
- Implementar conexão com API/serviço WhatsApp (Twilio, WhatsApp Business API, webhook).
- Autenticação, envio e recebimento de mensagens cruas.

Contratos esperados:
- Função send_message(to, payload)
- Endpoint webhook para receber mensagens

Variáveis de ambiente típicas:
- TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM

TODO:
- Adicionar exemplos de uso e snippets de autenticação.
