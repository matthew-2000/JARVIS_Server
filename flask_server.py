import os
import whisper
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Caricare le variabili d'ambiente
load_dotenv()

app = Flask(__name__)
model = whisper.load_model("large")

# Caricare API key da variabili d'ambiente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def transcribe_audio(audio_path):
    """Trascrive l'audio in testo usando Whisper."""
    try:
        result = model.transcribe(audio_path, language="it", temperature=0)
        return result.get("text", "Errore nella trascrizione")  # Restituisce solo il testo
    except Exception as e:
        return f"Errore: {str(e)}"

@app.route("/process_audio", methods=["POST"])
def process_audio():
    if "audio" not in request.files:
        return jsonify({"error": "Nessun file audio ricevuto"}), 400

    audio_file = request.files["audio"]
    audio_path = "temp_audio.wav"

    try:
        audio_file.save(audio_path)  # Salva il file temporaneamente
        text = transcribe_audio(audio_path)
        os.remove(audio_path)  # Rimuove il file dopo la trascrizione
        return jsonify({"transcription": text})
    except Exception as e:
        return jsonify({"error": f"Errore durante la trascrizione: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)