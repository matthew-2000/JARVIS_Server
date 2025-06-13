# server.py
import os
import json
import time
from datetime import datetime

from flask import Flask, request, jsonify
from dotenv import load_dotenv

# ───────────────────────── Components ──────────────────────────
from components.audio_processor import AudioProcessor
from components.emotion_recognizer import EmotionRecognizer
from components.chat_agent import ChatAgent
from components.ollama_chat_agent import OllamaChatAgent
from components.conversation_manager import ConversationManager
from components.orchestrator import Orchestrator

# ────────────────────────── Config ─────────────────────────────
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ENABLE_EMOTION_RECOGNITION = True          # abilita /disabilita endpoint audio
USE_LOCAL_MODEL           = False          # True = Ollama, False = OpenAI GPT-4o-mini

# ───────────────────────── Instances ───────────────────────────
app                = Flask(__name__)
audio_processor     = AudioProcessor()
emotion_recognizer  = EmotionRecognizer() if ENABLE_EMOTION_RECOGNITION else None
chat_agent          = OllamaChatAgent() if USE_LOCAL_MODEL else ChatAgent(api_key=OPENAI_API_KEY)
conv_manager        = ConversationManager()
orchestrator        = Orchestrator(chat_agent=chat_agent, conv_manager=conv_manager)

# ════════════════════════  ENDPOINTS  ══════════════════════════
@app.route("/detect_emotions", methods=["POST"])
def detect_emotions():
    """Riceve un file audio, restituisce le emozioni riconosciute."""
    if not emotion_recognizer:
        return jsonify({"error": "Riconoscimento emozioni disabilitato"}), 400
    if "audio" not in request.files:
        return jsonify({"error": "Nessun file audio ricevuto"}), 400

    audio_file = request.files["audio"]
    user_id    = request.form.get("user_id", "default_user")
    tmp_path   = "temp_audio.wav"

    try:
        audio_file.save(tmp_path)
        wav_path   = audio_processor.convert_to_wav(tmp_path) or tmp_path
        audio_arr  = audio_processor.load_audio(wav_path, max_duration_sec=30)
        emotions   = emotion_recognizer.predict(audio_arr)
        emotion_js = {e: f"{p:.2%}" for e, p in emotions}

        os.remove(tmp_path)
        return jsonify({"user_id": user_id, "emotions": emotion_js})

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/chat_message", methods=["POST"])
def chat_message():
    """
    Body JSON:
    {
      "user_id": "...",
      "text": "trascrizione dell'utente",
      "emotions": { "happy": "75.33%", ... }   #  facoltativo
    }
    """
    data     = request.get_json(silent=True) or {}
    user_id  = data.get("user_id", "default_user")
    text     = data.get("text", "").strip()
    emotions = data.get("emotions")            # può essere None

    if not text:
        return jsonify({"error": "Campo 'text' mancante"}), 400

    try:
        response = orchestrator.generate_response(user_id, text, emotions)
        save_conversation_to_file(user_id, text, emotions, response)
        return jsonify({"user_id": user_id, "response": response})

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/reset_conversation", methods=["POST"])
def reset_conversation():
    user_id = request.form.get("user_id", "default_user")
    conv_manager.reset(user_id)
    # bump session counter
    filename = f"conversations/{user_id}.json"
    if os.path.exists(filename):
        with open(filename, "r+", encoding="utf-8") as f:
            hist = json.load(f)
            hist["session_id"] = hist.get("session_id", 0) + 1
            f.seek(0); json.dump(hist, f, indent=4, ensure_ascii=False); f.truncate()
    else:
        os.makedirs("conversations", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({"user_id": user_id, "session_id": 1, "sessions": [[]]}, f, indent=4, ensure_ascii=False)
    return jsonify({"message": "Conversazione resettata."})


# ─────────────────── Persistenza su JSON ───────────────────────
def save_conversation_to_file(user_id, text, emotions, bot_response):
    os.makedirs("conversations", exist_ok=True)
    filename  = f"conversations/{user_id}.json"
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    entry = {
        "timestamp": timestamp,
        "transcription": text,
        "emotions": emotions or "Non rilevate",
        "chatgpt_response": bot_response
    }

    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = {"user_id": user_id, "session_id": 1, "sessions": [[]]}

        sess_idx = history.get("session_id", 1) - 1
        while len(history["sessions"]) <= sess_idx:
            history["sessions"].append([])
        history["sessions"][sess_idx].append(entry)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"[Server] Errore salvataggio conversazione: {e}")

# ─────────────────────────── Main ──────────────────────────────
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)