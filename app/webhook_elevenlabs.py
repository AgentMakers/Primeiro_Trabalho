from flask import Flask, request, jsonify
from integrations.whatsapp.storage import json_storage as storage

app = Flask(__name__)
DB_PATH = "./data/whatsapp_messages.jsonl"

@app.route("/webhook/elevenlabs", methods=["POST"])
def webhook_elevenlabs():
    payload = request.json or {}
    text = payload.get("text")
    user = payload.get("user") or "anonymous"
    session = payload.get("session") or user
    if not text:
        return jsonify({"ok": False, "error": "missing text"}), 400
    qid = storage.save_question(DB_PATH, user_id=user, session_id=session, channel="eleven_webhook", text=text)
    return jsonify({"ok": True, "qid": qid})

if __name__ == "__main__":
    # run on port 8001 for local testing
    app.run(host="0.0.0.0", port=8001)
