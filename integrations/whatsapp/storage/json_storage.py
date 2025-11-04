"""Simple JSONL storage for prototyping message persistence.

Each record is stored as a single JSON object per line (JSON Lines). This is
suitable for local development and small datasets.

API:
- init_store(path)
- save_question(path, ...)
- get_recent(path, user_id, n=10)
- get_session(path, session_id)
- set_tts_info(path, qid, audio_uri)
- set_embedding_id(path, qid, embedding_id)
- set_rag_result(path, qid, rag_result_id)

Note: updates (set_*) rewrite the file; acceptable for prototypes.
"""
from __future__ import annotations

import os
import json
import uuid
import datetime
from typing import Optional, List, Dict, Any


def _ensure_dir(path: str) -> None:
    d = os.path.dirname(os.path.abspath(path))
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def init_store(path: str) -> None:
    _ensure_dir(path)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8"):
            pass


def _read_all(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    items: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except Exception:
                # skip malformed lines
                continue
    return items


def _write_all(path: str, items: List[Dict[str, Any]]) -> None:
    _ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")


def save_question(
    path: str,
    user_id: str,
    session_id: str,
    channel: str,
    text: str,
    normalized_text: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    qid = str(uuid.uuid4())
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    record = {
        "id": qid,
        "user_id": user_id,
        "session_id": session_id,
        "channel": channel,
        "text": text,
        "normalized_text": normalized_text,
        "timestamp": timestamp,
        "embedding_id": None,
        "rag_result_id": None,
        "tts_generated": False,
        "audio_uri": None,
        "metadata": metadata or {},
    }
    _ensure_dir(path)
    # append as JSON line
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return qid


def get_recent(path: str, user_id: str, n: int = 10) -> List[Dict[str, Any]]:
    items = _read_all(path)
    filtered = [it for it in items if it.get("user_id") == user_id]
    # newest first
    filtered.sort(key=lambda x: x.get("timestamp") or "", reverse=True)
    return filtered[:n]


def get_session(path: str, session_id: str) -> List[Dict[str, Any]]:
    items = _read_all(path)
    filtered = [it for it in items if it.get("session_id") == session_id]
    filtered.sort(key=lambda x: x.get("timestamp") or "")
    return filtered


def _update_field(path: str, qid: str, **fields) -> bool:
    items = _read_all(path)
    updated = False
    for it in items:
        if it.get("id") == qid:
            for k, v in fields.items():
                it[k] = v
            updated = True
            break
    if updated:
        _write_all(path, items)
    return updated


def set_tts_info(path: str, qid: str, audio_uri: str) -> bool:
    return _update_field(path, qid, tts_generated=True, audio_uri=audio_uri)


def set_embedding_id(path: str, qid: str, embedding_id: str) -> bool:
    return _update_field(path, qid, embedding_id=embedding_id)


def set_rag_result(path: str, qid: str, rag_result_id: str) -> bool:
    return _update_field(path, qid, rag_result_id=rag_result_id)
