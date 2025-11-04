"""Agents Platform WebSocket client — capture user transcriptions in real-time and persist to SQLite.

Saves events of type `user_transcript` and `user_message` into the repository's
SQLite storage (`integrations.whatsapp.storage.sqlite_storage`).

Features:
- reconnect with exponential backoff
- capture conversation_id from conversation_initiation_metadata
- save minimal info (session_id, user_id, text, timestamp, raw_event)

Usage (PowerShell):
  $env:ELEVENLABS_API_KEY = 'your_key'
  $env:AGENT_ID = 'your_agent_id'
  python integrations/elevenlabs/clients/agents_ws_text_capture.py

Dependencies:
  pip install websockets

Notes:
- This script writes into SQLite at ./data/whatsapp_storage.db by default.
- It writes immediately on receipt of relevant events; audio chunks are ignored.
"""
from __future__ import annotations

import os
import asyncio
import json
import time
import logging
from typing import Optional

import websockets

from integrations.whatsapp.storage import sqlite_storage as storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

API_KEY = os.getenv("ELEVENLABS_API_KEY")
AGENT_ID = os.getenv("AGENT_ID")
DB_PATH = os.getenv("WHATSAPP_DB_PATH") or "./data/whatsapp_storage.db"

WS_TEMPLATE = "wss://api.elevenlabs.io/v1/convai/conversation?agent_id={agent_id}"


def _build_ws_url(agent_id: str) -> str:
    return WS_TEMPLATE.format(agent_id=agent_id)


async def _handle_message(msg: str, conversation_id_holder: dict) -> None:
    try:
        data = json.loads(msg)
    except Exception:
        return
    typ = data.get("type")

    # conversation id
    if typ == "conversation_initiation_metadata":
        meta = data.get("conversation_initiation_metadata", {})
        conv_id = meta.get("conversation_id")
        if conv_id:
            conversation_id_holder["conversation_id"] = conv_id
            logger.info("Conversation started: %s", conv_id)
        return

    # user transcript event
    if typ == "user_transcript":
        ev = data.get("user_transcription_event", {})
        text = ev.get("user_transcript")
        if text:
            session = conversation_id_holder.get("conversation_id") or "unknown"
            # save to sqlite
            storage.init_db(DB_PATH)
            storage.save_question(DB_PATH, user_id=ev.get("user_id") or "eleven_user", session_id=session, channel="eleven_agents_ws", text=text, metadata={"raw_event": data})
            logger.info("Saved user_transcript: %s", text[:80])
        return

    # user_message (non-transcription textual message)
    if typ == "user_message":
        text = data.get("text") or (data.get("user_message") or {}).get("text")
        if text:
            session = conversation_id_holder.get("conversation_id") or "unknown"
            storage.init_db(DB_PATH)
            storage.save_question(DB_PATH, user_id=data.get("user_id") or "eleven_user", session_id=session, channel="eleven_agents_ws", text=text, metadata={"raw_event": data})
            logger.info("Saved user_message: %s", text[:80])
        return


async def _consumer_loop(uri: str, headers: list):
    backoff = 1
    max_backoff = 60
    conversation_id_holder = {}

    while True:
        try:
            logger.info("Connecting to %s", uri)
            async with websockets.connect(uri, extra_headers=headers, ping_interval=20, ping_timeout=10) as ws:
                logger.info("Connected")
                backoff = 1
                async for message in ws:
                    await _handle_message(message, conversation_id_holder)
        except Exception as e:
            logger.warning("Connection error: %s", e)
            logger.info("Reconnecting in %s seconds...", backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, max_backoff)


def main():
    if not API_KEY:
        logger.error("ELEVENLABS_API_KEY not set")
        return
    if not AGENT_ID:
        logger.error("AGENT_ID not set")
        return

    uri = _build_ws_url(AGENT_ID)
    headers = [("xi-api-key", API_KEY)]

    # ensure DB exists
    storage.init_db(DB_PATH)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_consumer_loop(uri, headers))
    except KeyboardInterrupt:
        logger.info("Interrupted by user")


if __name__ == "__main__":
    main()
