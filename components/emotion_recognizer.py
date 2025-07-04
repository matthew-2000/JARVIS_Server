# components/emotion_recognizer.py
import torch
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor

class EmotionRecognizer:
    """Riconoscimento emozioni vocali tramite modello HuggingFace."""
    def __init__(self, model_id="firdhokk/speech-emotion-recognition-with-openai-whisper-large-v3"):
        self.model      = AutoModelForAudioClassification.from_pretrained(model_id)
        self.extractor  = AutoFeatureExtractor.from_pretrained(model_id, do_normalize=True)
        self.id2label   = self.model.config.id2label
        self.device     = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device).eval()

    def predict(self, audio_array):
        """Ritorna lista (label, prob) ordinata discendente."""
        inputs = self.extractor(audio_array, sampling_rate=self.extractor.sampling_rate, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            logits = self.model(**inputs).logits
        probs = torch.nn.functional.softmax(logits, dim=-1).squeeze().tolist()
        return sorted([(self.id2label[i], p) for i, p in enumerate(probs)], key=lambda x: x[1], reverse=True)