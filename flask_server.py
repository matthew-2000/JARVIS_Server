# server.py  – Flask server con debug verbose
import os, json, time
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# ─── Componenti locali ──────────────────────────────────────────
from components.audio_processor     import AudioProcessor
from components.audio_accumulator   import AudioAccumulator
from components.emotion_recognizer  import EmotionRecognizer
from components.chat_agent          import ChatAgent
from components.ollama_chat_agent   import OllamaChatAgent
from components.conversation_manager import ConversationManager
from components.orchestrator        import Orchestrator
from components.emotion_memory      import EmotionMemory

# ─── Config ─────────────────────────────────────────────────────
load_dotenv()
OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY")
ENABLE_EMO_ENDPOINT = True
USE_LOCAL_MODEL     = False   # True → Ollama, False → OpenAI
EMO_TTL_SEC         = 30      # “freschezza” emozioni
ACCUM_THRESHOLD_SEC = 25      # audio tot. prima di inferire

# ─── Helpers log ────────────────────────────────────────────────
def log(msg, user_id="system"):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] [{user_id}] {msg}")

# ─── Instanzia moduli ───────────────────────────────────────────
app               = Flask(__name__)
audio_proc        = AudioProcessor()
accum             = AudioAccumulator(threshold_sec=ACCUM_THRESHOLD_SEC)
emo_rec           = EmotionRecognizer() if ENABLE_EMO_ENDPOINT else None
chat_agent        = OllamaChatAgent() if USE_LOCAL_MODEL else ChatAgent(api_key=OPENAI_API_KEY)
conv_mgr          = ConversationManager()
emo_mem           = EmotionMemory(ttl_sec=EMO_TTL_SEC)
orchestrator      = Orchestrator(chat_agent, conv_mgr, emo_mem)

# ════════════════════════ ENDPOINTS ════════════════════════════
@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    if not emo_rec:
        return jsonify({"error": "Riconoscimento emozioni disabilitato"}), 400
    if "audio" not in request.files:
        return jsonify({"error": "Manca il file audio"}), 400

    user_id  = request.form.get("user_id", "default_user")
    tmp_path = "temp_audio.wav"
    request.files["audio"].save(tmp_path)
    log("Audio chunk ricevuto.", user_id)

    try:
        wav_path  = audio_proc.convert_to_wav(tmp_path) or tmp_path
        chunk_arr = audio_proc.load_audio(wav_path, 30)
        dur = len(chunk_arr) / 16_000
        log(f"Aggiungo {dur:.2f}s al buffer.", user_id)

        accum.add_chunk(user_id, chunk_arr)
        total_dur = accum.threshold * (sum(len(b) for b in accum._buffers[user_id]) / (accum.threshold * 16_000))
        log(f"Durata buffer: {total_dur:.2f}/{ACCUM_THRESHOLD_SEC}s.", user_id)

        if not accum.should_infer(user_id):
            return jsonify({"status": "buffering"})

        # inferenza
        full_arr = accum.pop_concat(user_id)
        log(f"Inizio inferenza emozioni su {len(full_arr)/16_000:.2f}s audio…", user_id)
        emotions = emo_rec.predict(full_arr)
        emo_dict = {e: f"{p:.2%}" for e, p in emotions}
        log(f"Emozioni → {emo_dict}", user_id)
        emo_mem.update(user_id, emo_dict)

        return jsonify({"status": "inferred", "emotions": emo_dict})
    except Exception as e:
        log(f"Errore upload_audio: {e}", user_id)
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(tmp_path)

@app.route("/chat_message", methods=["POST"])
def chat_message():
    data    = request.get_json(silent=True) or {}
    user_id = data.get("user_id", "default_user")
    text    = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Campo 'text' mancante"}), 400

    log(f"Prompt ricevuto: «{text}»", user_id)
    try:
        response = orchestrator.generate_response(user_id, text)
        log(f"Risposta LLM: «{response[:80]}…»", user_id)
        save_turn(user_id, text, response)
        return jsonify({"user_id": user_id, "response": response})
    except Exception as e:
        log(f"Errore chat_message: {e}", user_id)
        return jsonify({"error": str(e)}), 500

@app.route("/reset_conversation", methods=["POST"])
def reset_conversation():
    user_id = request.form.get("user_id", "default_user")
    conv_mgr.reset(user_id); emo_mem.reset(user_id); accum.pop_concat(user_id)
    bump_session_file(user_id)
    log("Reset conversazione.", user_id)
    return jsonify({"message": "Conversazione resettata."})

# ─── Persistenza JSON ───────────────────────────────────────────
def bump_session_file(user_id):
    filename = f"conversations/{user_id}.json"
    os.makedirs("conversations", exist_ok=True)
    if os.path.exists(filename):
        with open(filename, "r+", encoding="utf-8") as f:
            hist = json.load(f); hist["session_id"] = hist.get("session_id",0)+1
            f.seek(0); json.dump(hist, f, indent=2, ensure_ascii=False); f.truncate()
    else:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({"user_id":user_id,"session_id":1,"sessions":[[]]}, f, indent=2, ensure_ascii=False)

def save_turn(user_id, text, bot_response):
    filename = f"conversations/{user_id}.json"
    os.makedirs("conversations", exist_ok=True)
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H-%M-%S"),
        "transcription": text,
        "emotions": emo_mem.get_recent(user_id) or "Non rilevate",
        "chatgpt_response": bot_response
    }
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f: hist = json.load(f)
    else:
        hist = {"user_id": user_id, "session_id": 1, "sessions": [[]]}
    idx = hist.get("session_id",1)-1
    while len(hist["sessions"]) <= idx: hist["sessions"].append([])
    hist["sessions"][idx].append(entry)
    with open(filename, "w", encoding="utf-8") as f: json.dump(hist, f, indent=2, ensure_ascii=False)

# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log("Server in avvio…")
    app.run(host="127.0.0.1", port=5001, debug=True)
