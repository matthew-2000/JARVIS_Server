import os
import time

from flask import Flask, request, jsonify
from dotenv import load_dotenv
import json
from datetime import datetime

# Import delle classi dal package
from components.audio_processor import AudioProcessor
from components.emotion_recognizer import EmotionRecognizer
from components.transcriber import Transcriber
from components.chat_model_interface import ChatModelInterface
from components.ollama_chat_agent import OllamaChatAgent
from components.chat_agent import ChatAgent
from components.conversation_manager import ConversationManager
from components.audio_interaction_service import AudioInteractionService

# Suppress warnings from transformers
import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Carica le variabili d'ambiente
load_dotenv()

# Configurazioni
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ENABLE_EMOTION_RECOGNITION = True
emotion_recognition_enabled = ENABLE_EMOTION_RECOGNITION

# Inizializza Flask
app = Flask(__name__)

# Inizializza i componenti
processor = AudioProcessor()
recognizer = EmotionRecognizer() if ENABLE_EMOTION_RECOGNITION else None
transcriber = Transcriber()

USE_LOCAL_MODEL = False  # cambia questo valore per usare OpenAI (false) oppure Ollama (true)

if USE_LOCAL_MODEL:
    chat_agent = OllamaChatAgent(model_name="llama3.2")
else:
    chat_agent = ChatAgent(api_key=OPENAI_API_KEY)

conversation_manager = ConversationManager()

# Servizio che coordina tutto
service = AudioInteractionService(
    processor=processor,
    recognizer=recognizer,
    transcriber=transcriber,
    chat_agent=chat_agent,
    conv_manager=conversation_manager
)


@app.route("/process_audio", methods=["POST"])
def process_audio():
    if "audio" not in request.files:
        return jsonify({"error": "Nessun file audio ricevuto"}), 400

    audio_file = request.files["audio"]
    user_id = request.form.get("user_id", "default_user")
    audio_path = "temp_audio.wav"

    try:
        # Salva l'audio
        audio_file.save(audio_path)
        print(f"[Server] Ricevuto file audio da user_id: {user_id}")

        print("[Server] Inizio elaborazione audio...")

        start_time = time.time()
        result = service.process_audio(user_id, audio_path, emotion_recognition_enabled)
        end_time = time.time()

        print(f"[Server] Tempo totale elaborazione: {end_time - start_time:.2f} secondi")

        print("[Server] Elaborazione completata.")
        save_conversation_to_file(user_id, result)
        print(f"[Server] Risultato: {result}")

        # Pulisci
        os.remove(audio_path)

        return jsonify(result)

    except Exception as e:
        print(f"[Server] Errore durante l'elaborazione: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/reset_conversation", methods=["POST"])
def reset_conversation():
    user_id = request.form.get("user_id", "default_user")
    conversation_manager.reset(user_id)
    print(f"[Server] Conversazione resettata per user_id: {user_id}")
    # Aggiungi tag sessione nuova
    filename = f"conversations/{user_id}.json"
    if os.path.exists(filename):
        with open(filename, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data["session_id"] = data.get("session_id", 0) + 1
            f.seek(0)
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.truncate()
    else:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({"user_id": user_id, "session_id": 1, "sessions": [[]]}, f, indent=4, ensure_ascii=False)
    return jsonify({"message": f"Conversazione per '{user_id}' resettata."}), 200

@app.route("/set_emotion_enabled", methods=["POST"])
def set_emotion_enabled():
    global emotion_recognition_enabled
    val = request.form.get("enabled", "").lower()
    if val == "true":
        emotion_recognition_enabled = True
        print("[Server] Riconoscimento emozioni abilitato.")
    elif val == "false":
        emotion_recognition_enabled = False
        print("[Server] Riconoscimento emozioni disabilitato.")
    else:
        return jsonify({"error": "Valore non valido. Usa 'true' o 'false'."}), 400
    return jsonify({"enabled": emotion_recognition_enabled})


# Salva la conversazione
def save_conversation_to_file(user_id, result):
    os.makedirs("conversations", exist_ok=True)
    filename = f"conversations/{user_id}.json"
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

    entry = {
        "timestamp": timestamp,
        "transcription": result.get("transcription"),
        "emotions": result.get("emotions"),
        "chatgpt_response": result.get("chatgpt_response")
    }

    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                history = json.load(f)
        else:
            history = {"user_id": user_id, "session_id": 1, "sessions": [[]]}

        # Ensure structure
        if "sessions" not in history or not isinstance(history["sessions"], list):
            history["sessions"] = [[]]

        current_session_index = history.get("session_id", 1) - 1
        while len(history["sessions"]) <= current_session_index:
            history["sessions"].append([])

        history["sessions"][current_session_index].append(entry)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4, ensure_ascii=False)

        print(f"[Server] Conversazione aggiornata in {filename}")
    except Exception as e:
        print(f"[Server] Errore salvataggio conversazione: {e}")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)