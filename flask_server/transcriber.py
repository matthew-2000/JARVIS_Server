import whisper

# Caricare il modello Whisper
model = whisper.load_model("large")

def transcribe_audio(audio_path):
    """Trascrive l'audio in testo usando Whisper."""
    try:
        result = model.transcribe(audio_path, language="it", temperature=0)
        return result.get("text", "Errore nella trascrizione")  # Restituisce solo il testo
    except Exception as e:
        return f"Errore: {str(e)}"
