"""SQLite storage helper for saving user questions and metadata.

This module provides a small, dependency-free wrapper around sqlite3 to store
user messages/questions, RAG/embedding references and TTS output metadata.

Usage:
    from integrations.whatsapp.storage import sqlite_storage as storage

    db = "./data/whatsapp_storage.db"
    storage.init_db(db)
    qid = storage.save_question(db, user_id="user-123", session_id="sess-1", channel="whatsapp", text="Olá, preciso de ajuda")
    recent = storage.get_recent(db, "user-123", n=5)

The module keeps metadata as JSON text. It's intended for local development/prototyping.
"""
from __future__ import annotations

import sqlite3
import uuid
import datetime
import json
from typing import Optional, List, Dict, Any

DEFAULT_SCHEMA = """
CREATE TABLE IF NOT EXISTS user_questions (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    session_id TEXT,
    channel TEXT,
    text TEXT,
    normalized_text TEXT,
    timestamp TEXT,
    embedding_id TEXT,
    rag_result_id TEXT,
    tts_generated INTEGER DEFAULT 0,
    audio_uri TEXT,
    metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_user_timestamp ON user_questions (user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_session_timestamp ON user_questions (session_id, timestamp);
"""


def _get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    """Create tables and indexes if they don't exist."""
    conn = _get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.executescript(DEFAULT_SCHEMA)
        conn.commit()
    finally:
        conn.close()


def save_question(
    db_path: str,
    user_id: str,
    session_id: str,
    channel: str,
    text: str,
    normalized_text: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Insert a question record and return the generated id."""
    qid = str(uuid.uuid4())
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    meta_json = json.dumps(metadata or {})

    conn = _get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO user_questions (id, user_id, session_id, channel, text, normalized_text, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (qid, user_id, session_id, channel, text, normalized_text, timestamp, meta_json),
        )
        conn.commit()
    finally:
        conn.close()

    return qid


def get_recent(db_path: str, user_id: str, n: int = 10) -> List[Dict[str, Any]]:
    """Return the most recent n questions for a user (newest first)."""
    conn = _get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM user_questions WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, n),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_session(db_path: str, session_id: str) -> List[Dict[str, Any]]:
    """Return all question records for a session ordered by timestamp ascending."""
    conn = _get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM user_questions WHERE session_id = ? ORDER BY timestamp ASC",
            (session_id,),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def set_tts_info(db_path: str, qid: str, audio_uri: str) -> bool:
    """Mark a record as having generated TTS audio and store the audio URI."""
    conn = _get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE user_questions SET tts_generated = 1, audio_uri = ? WHERE id = ?",
            (audio_uri, qid),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def set_embedding_id(db_path: str, qid: str, embedding_id: str) -> bool:
    """Associate an embedding id (from vector DB) with a question record."""
    conn = _get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE user_questions SET embedding_id = ? WHERE id = ?",
            (embedding_id, qid),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def set_rag_result(db_path: str, qid: str, rag_result_id: str) -> bool:
    conn = _get_conn(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE user_questions SET rag_result_id = ? WHERE id = ?",
            (rag_result_id, qid),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
