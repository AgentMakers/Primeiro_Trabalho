"""Twilio connector skeleton
Responsabilidade: enviar/receber mensagens via Twilio WhatsApp API
"""
from typing import Dict, Any
import os

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")

class TwilioConnector:
    def __init__(self, account_sid: str = None, auth_token: str = None, whatsapp_from: str = None):
        self.account_sid = account_sid or TWILIO_ACCOUNT_SID
        self.auth_token = auth_token or TWILIO_AUTH_TOKEN
        self.whatsapp_from = whatsapp_from or TWILIO_WHATSAPP_FROM

    def send_message(self, to: str, body: str, media: Any = None) -> Dict[str, Any]:
        """Enviar texto/media para um número via WhatsApp (Twilio).
        Implementação real deve usar twilio.Client.
        """
        # placeholder
        return {"to": to, "body": body, "status": "mocked"}

    def validate_config(self) -> bool:
        return all([self.account_sid, self.auth_token, self.whatsapp_from])
