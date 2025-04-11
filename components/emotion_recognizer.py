import torch
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor

class EmotionRecognizer:
    def __init__(self, model_id="firdhokk/speech-emotion-recognition-with-openai-whisper-large-v3"):
        self.model = AutoModelForAudioClassification.from_pretrained(model_id)
        self.extractor = AutoFeatureExtractor.from_pretrained(model_id, do_normalize=True)
        self.id2label = self.model.config.id2label
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def predict(self, audio_array):
        inputs = self.extractor(audio_array, sampling_rate=self.extractor.sampling_rate, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            logits = self.model(**inputs).logits
        probs = torch.nn.functional.softmax(logits, dim=-1).squeeze().tolist()

        return sorted([(self.id2label[i], prob) for i, prob in enumerate(probs)], key=lambda x: x[1], reverse=True)