import os, json, time, math
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from collections import defaultdict

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
ENABLE_EMO_ENDPOINT = True    # True → abilita endpoint emozioni
USE_LOCAL_MODEL     = False   # True → Ollama, False → OpenAI
EMO_TTL_SEC         = 90      # “freschezza” emozioni
ACCUM_THRESHOLD_SEC = 25      # audio tot. prima di inferire

# ─── Metriche runtime ──────────────────────────────────────────
module_latencies = {}          # user_id → {"wav":..,"emo":..}
audio_stats      = {}          # user_id → {"chunk_duration_ms":..}
reset_counter    = defaultdict(int)  # user_id → count

# ─── Helpers log ────────────────────────────────────────────────
def log(msg, user_id="system"):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] [{user_id}] {msg}")

# ─── Instanzia moduli ───────────────────────────────────────────
log("Avvio server...")
app               = Flask(__name__)
audio_proc        = AudioProcessor()
accum             = AudioAccumulator(threshold_sec=ACCUM_THRESHOLD_SEC)
emo_rec           = EmotionRecognizer() if ENABLE_EMO_ENDPOINT else None
chat_agent        = OllamaChatAgent() if USE_LOCAL_MODEL else ChatAgent(api_key=OPENAI_API_KEY)
conv_mgr          = ConversationManager()
emo_mem           = EmotionMemory(ttl_sec=EMO_TTL_SEC)
orchestrator      = Orchestrator(chat_agent, conv_mgr, emo_mem)

log("Componenti inizializzati con successo.")

# ════════════════════════ ENDPOINTS ════════════════════════════
@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    log("Richiesta POST ricevuta su /upload_audio", user_id=request.form.get("user_id", "default_user"))

    if not emo_rec:
        log("Riconoscimento emozioni disabilitato", user_id=request.form.get("user_id", "default_user"))
        return jsonify({"error": "Riconoscimento emozioni disabilitato"}), 400
    if "audio" not in request.files:
        log("Manca il file audio", user_id=request.form.get("user_id", "default_user"))
        return jsonify({"error": "Manca il file audio"}), 400

    user_id  = request.form.get("user_id", "default_user")
    tmp_path = "temp_audio.wav"
    request.files["audio"].save(tmp_path)
    log("Audio chunk ricevuto.", user_id)

    try:
        t_start = time.time()
        wav_path  = audio_proc.convert_to_wav(tmp_path) or tmp_path
        wav_ms = (time.time()-t_start)*1000
        log(f"Audio convertito in WAV. Percorso: {wav_path}", user_id)

        chunk_arr = audio_proc.load_audio(wav_path, 30)
        dur = len(chunk_arr) / 16_000
        log(f"Aggiungo {dur:.2f}s al buffer.", user_id)

        accum.add_chunk(user_id, chunk_arr)
        total_dur = accum.threshold * (sum(len(b) for b in accum._buffers[user_id]) / (accum.threshold * 16_000))
        log(f"Durata buffer: {total_dur:.2f}/{ACCUM_THRESHOLD_SEC}s.", user_id)

        if not accum.should_infer(user_id):
            log("Buffering non completato, attesa...", user_id)
            return jsonify({"status": "buffering"})

        # inferenza
        full_arr = accum.pop_concat(user_id)
        log(f"Inizio inferenza emozioni su {len(full_arr)/16_000:.2f}s audio…", user_id)
        t_emo_start = time.time()
        emotions = emo_rec.predict(full_arr)
        emo_ms = (time.time()-t_emo_start)*1000
        chunk_ms = len(full_arr)/16_000*1000
        probs_float = {e: p for e, p in emotions}
        top_emotion = max(probs_float, key=probs_float.get)
        entropy     = -sum(p * math.log2(p) for p in probs_float.values())
        emo_dict = {
            "probs": probs_float,
            "top_emotion": top_emotion,
            "entropy": entropy,
            "emo_timestamp": datetime.utcnow().isoformat(),
            "chunk_duration_ms": chunk_ms
        }
        log(f"Emozioni inferite → {emo_dict}", user_id)
        emo_mem.update(user_id, emo_dict)

        audio_stats[user_id] = {"chunk_duration_ms": chunk_ms}
        module_latencies[user_id] = {"wav": wav_ms, "emo": emo_ms}

        return jsonify({"status": "inferred", "emotions": emo_dict})
    except Exception as e:
        log(f"Errore durante l'elaborazione audio: {e}", user_id)
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(tmp_path)
        log(f"File temporaneo rimosso: {tmp_path}", user_id)

@app.route("/chat_message", methods=["POST"])
def chat_message():
    log("Richiesta POST ricevuta su /chat_message", user_id=request.get_json().get("user_id", "default_user"))

    data    = request.get_json(silent=True) or {}
    user_id = data.get("user_id", "default_user")
    text    = data.get("text", "").strip()

    words = len(text.split())
    chars = len(text)

    if not text:
        log("Campo 'text' mancante nella richiesta", user_id)
        return jsonify({"error": "Campo 'text' mancante"}), 400

    log(f"Prompt ricevuto: «{text}»", user_id)
    try:
        response_text, llm_meta = orchestrator.generate_response(user_id, text)
        lat = module_latencies.get(user_id, {}).copy()
        lat["llm"] = llm_meta.get("llm_latency_ms")
        log(f"Risposta LLM generata: «{response_text[:80]}…»", user_id)
        save_turn(user_id, text, response_text, llm_meta, words, chars, lat)
        return jsonify({"user_id": user_id, "response": response_text})
    except Exception as e:
        log(f"Errore durante la generazione della risposta LLM: {e}", user_id)
        return jsonify({"error": str(e)}), 500

@app.route("/reset_conversation", methods=["POST"])
def reset_conversation():
    log("Richiesta POST ricevuta su /reset_conversation", user_id=request.form.get("user_id", "default_user"))
    user_id = request.form.get("user_id", "default_user")
    conv_mgr.reset(user_id)
    emo_mem.reset(user_id)
    accum.pop_concat(user_id)
    bump_session_file(user_id)
    reset_counter[user_id] += 1
    log("Conversazione resettata.", user_id)
    return jsonify({"message": "Conversazione resettata."})

# ─── Persistenza JSON ───────────────────────────────────────────
def bump_session_file(user_id):
    log(f"Verifica file di sessione per {user_id}...", user_id)
    filename = f"conversations/{user_id}.json"
    os.makedirs("conversations", exist_ok=True)
    if os.path.exists(filename):
        with open(filename, "r+", encoding="utf-8") as f:
            hist = json.load(f)
            hist["session_id"] = hist.get("session_id", 0) + 1
            # Assicuriamo che esista un array per la nuova sessione
            while len(hist.get("sessions", [])) < hist["session_id"]:
                hist["sessions"].append([])
            f.seek(0)
            json.dump(hist, f, indent=2, ensure_ascii=False)
            f.truncate()
        log(f"Sessione aggiornata per {user_id}", user_id)
    else:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({"user_id": user_id, "session_id": 1, "sessions": [[]]}, f, indent=2, ensure_ascii=False)
        log(f"Nuovo file di sessione creato per {user_id}", user_id)

def save_turn(user_id, text, bot_response, llm_meta, words, chars, latencies):
    filename = f"conversations/{user_id}.json"
    now_dt   = datetime.now()
    now_str  = now_dt.strftime("%Y-%m-%dT%H-%M-%S")

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            hist = json.load(f)
    else:
        hist = {"user_id": user_id, "session_id": 1, "sessions": [[]]}

    idx = hist.get("session_id", 1) - 1
    while len(hist["sessions"]) <= idx:
        hist["sessions"].append([])

    last_ts = None
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            tmp_hist = json.load(f)
        sess_idx = tmp_hist.get("session_id", 1) - 1
        if sess_idx < len(tmp_hist.get("sessions", [])) and tmp_hist["sessions"][sess_idx]:
            last_ts = tmp_hist["sessions"][sess_idx][-1]["timestamp"]
    delta_prev_ms = None
    if last_ts:
        last_dt = datetime.strptime(last_ts, "%Y-%m-%dT%H-%M-%S")
        delta_prev_ms = int((now_dt - last_dt).total_seconds() * 1000)

    turn_id = len(hist["sessions"][idx]) + 1

    entry = {
        "timestamp": now_str,
        "session_id": hist.get("session_id", 1),
        "turn_id": turn_id,
        "delta_prev_ms": delta_prev_ms,
        "transcription": text,
        "words": words,
        "chars": chars,
        "emotions": emo_mem.get_recent(user_id) or "Non rilevate",
        "llm": llm_meta,
        "latencies_ms": latencies,
        "reset_count": reset_counter.get(user_id, 0),
        "llm_response": bot_response
    }

    hist["sessions"][idx].append(entry)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(hist, f, indent=2, ensure_ascii=False)
    log(f"Turno salvato per {user_id}", user_id)

# ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log("Server in avvio…")
    app.run(host="0.0.0.0", port=5001, debug=True)