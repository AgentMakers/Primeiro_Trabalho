"""Connect to ElevenLabs multi-stream WebSocket, relay text, and persist only text messages.

Usage (PowerShell):
  $env:ELEVENLABS_API_KEY = 'your_key'
  $env:VOICE_ID = 'your_voice_id'
  python integrations/elevenlabs/clients/tts_multi_ws_text_capture.py

Behavior:
- Reads lines from stdin (type Enter) and sends them as sendText messages to the WS.
- Saves every outgoing text (user) to storage and also saves any incoming textual messages
  found in server messages (if present). Audio chunks are ignored.

Note: requires `websockets` package (pip install websockets).
"""
from __future__ import annotations

import asyncio
import json
import os
import uuid
import datetime
import websockets
from typing import Optional

# choose storage implementation: json_storage or sqlite_storage
from integrations.whatsapp.storage import json_storage as storage

API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID") or "default"
DB_PATH = os.getenv("WHATSAPP_DB_PATH") or "./data/whatsapp_messages.jsonl"

WS_URL = f"wss://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/multi-stream-input"


def save_outgoing(text: str, user_id: str = "local-user", session_id: Optional[str] = None) -> str:
    session = session_id or user_id
    qid = storage.save_question(DB_PATH, user_id=user_id, session_id=session, channel="eleven_ws_out", text=text)
    return qid


def save_incoming(text: str, user_id: str = "eleven", session_id: Optional[str] = None) -> str:
    session = session_id or user_id
    qid = storage.save_question(DB_PATH, user_id=user_id, session_id=session, channel="eleven_ws_in", text=text)
    return qid


async def consumer_handler(ws: websockets.WebSocketClientProtocol):
    async for msg in ws:
        try:
            data = json.loads(msg)
        except Exception:
            # not JSON - ignore
            continue

        # ignore audioOutput messages
        mtype = data.get("type")
        if mtype == "audioOutput":
            continue

        # If message contains textual payload, save it.
        # Docs vary — handle common fields conservatively.
        text = None
        if "text" in data and isinstance(data.get("text"), str):
            text = data.get("text").strip()
        # some responses may include 'transcript' or 'finalTranscript'
        if not text:
            for key in ("transcript", "finalTranscript", "speechToText", "recognizedText"):
                if key in data and isinstance(data.get(key), str):
                    text = data.get(key).strip()
                    break

        if text:
            save_incoming(text)


async def producer_handler(ws: websockets.WebSocketClientProtocol):
    # initialize connection message (adjust as needed)
    init_msg = {"type": "initializeConnection", "voice_settings": {"speed": 1.0, "stability": 0.5}}
    await ws.send(json.dumps(init_msg))

    print("Connected. Type lines to send as text to ElevenLabs (Ctrl+C to exit).")
    loop = asyncio.get_event_loop()
    while True:
        # read line from stdin without blocking the event loop
        text = await loop.run_in_executor(None, lambda: input("> "))
        if not text:
            continue
        # save outgoing text locally
        save_outgoing(text)
        # send as sendText message
        send_msg = {"type": "sendText", "text": text, "try_trigger_generation": True}
        await ws.send(json.dumps(send_msg))


async def run():
    if not API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY environment variable is required")

    headers = [("xi-api-key", API_KEY)]
    async with websockets.connect(WS_URL, extra_headers=headers) as ws:
        consumer_task = asyncio.create_task(consumer_handler(ws))
        producer_task = asyncio.create_task(producer_handler(ws))
        done, pending = await asyncio.wait([consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED)
        for t in pending:
            t.cancel()


if __name__ == "__main__":
    # ensure storage exists
    storage.init_store(DB_PATH)  # json_storage defines init_store
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print("Error:", e)
