import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from transcriber import transcribe_audio
from emotion_recognition import predict_emotion

# Caricare le variabili d'ambiente
load_dotenv()

app = Flask(__name__)

# Configurazione: Attivare/disattivare il riconoscimento delle emozioni
ENABLE_EMOTION_RECOGNITION = True  # Cambia in False se non vuoi riconoscere emozioni

@app.route("/process_audio", methods=["POST"])
def process_audio():
    if "audio" not in request.files:
        return jsonify({"error": "Nessun file audio ricevuto"}), 400

    audio_file = request.files["audio"]
    audio_path = "temp_audio.wav"

    try:
        # Salva il file temporaneamente
        audio_file.save(audio_path)

        # Trascrizione
        text = transcribe_audio(audio_path)

        response = {"transcription": text}

        # Se il riconoscimento delle emozioni è attivo
        if ENABLE_EMOTION_RECOGNITION:
            emotions = predict_emotion(audio_path)
            if emotions:
                response["emotions"] = {emotion: f"{score:.2%}" for emotion, score in emotions}
            else:
                response["emotions"] = "Errore nel riconoscimento delle emozioni"

        # Rimuovere il file audio temporaneo
        os.remove(audio_path)

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": f"Errore durante l'elaborazione: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)