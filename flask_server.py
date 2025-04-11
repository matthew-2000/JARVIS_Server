import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import concurrent.futures

# Import delle classi modulari dal package
from components.audio_processor import AudioProcessor
from components.emotion_recognizer import EmotionRecognizer
from components.transcriber import Transcriber
from components.chat_agent import ChatAgent
from components.conversation_manager import ConversationManager
from components.audio_interaction_service import AudioInteractionService

# Carica le variabili d'ambiente
load_dotenv()

# Configurazioni
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ENABLE_EMOTION_RECOGNITION = True  # Può essere dinamico in futuro
emotion_recognition_enabled = ENABLE_EMOTION_RECOGNITION

# Inizializza Flask
app = Flask(__name__)

# Inizializza i componenti
processor = AudioProcessor()
recognizer = EmotionRecognizer() if ENABLE_EMOTION_RECOGNITION else None
transcriber = Transcriber()
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
        # Esegui il processamento in parallelo (opzionale, ma utile se serve estendere)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_result = executor.submit(service.process_audio, user_id, audio_path, emotion_recognition_enabled)
            result = future_result.result(timeout=60)

        print("[Server] Elaborazione completata.")
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

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)