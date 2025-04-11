import whisper

class Transcriber:
    def __init__(self, model_size="large"):
        self.model = whisper.load_model(model_size)

    def transcribe(self, path):
        try:
            result = self.model.transcribe(path, language="it", temperature=0)
            return result.get("text", "Errore")
        except Exception as e:
            print(f"[Transcriber] Errore: {e}")
            return f"Errore: {str(e)}"
