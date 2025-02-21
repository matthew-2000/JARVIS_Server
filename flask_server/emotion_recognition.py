import subprocess
import os
import torch
import numpy as np
import soundfile as sf
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor

# Caricare il modello
model_id = "firdhokk/speech-emotion-recognition-with-openai-whisper-large-v3"
model = AutoModelForAudioClassification.from_pretrained(model_id)
feature_extractor = AutoFeatureExtractor.from_pretrained(model_id, do_normalize=True)
id2label = model.config.id2label

def convert_mp3_to_wav(audio_path):
    """ Converte un file MP3 in WAV usando ffmpeg """
    wav_path = os.path.splitext(audio_path)[0] + ".wav"
    try:
        subprocess.run(["ffmpeg", "-y", "-i", audio_path, "-ac", "1", "-ar", "16000", wav_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return wav_path
    except Exception as e:
        print(f"❌ Errore nella conversione MP3 -> WAV: {e}")
        return None

def preprocess_audio(audio_path, feature_extractor, max_duration=30.0):
    """ Prepara l'audio per il modello """
    try:
        audio_array, sampling_rate = sf.read(audio_path)
    except Exception as e:
        print(f"❌ Errore nella lettura dell'audio: {e}")
        return None

    max_length = int(feature_extractor.sampling_rate * max_duration)
    if len(audio_array) > max_length:
        audio_array = audio_array[:max_length]
    else:
        audio_array = np.pad(audio_array, (0, max_length - len(audio_array)), mode='reflect')

    max_val = np.max(np.abs(audio_array))
    if max_val > 0:
        audio_array = audio_array / max_val

    inputs = feature_extractor(audio_array, sampling_rate=feature_extractor.sampling_rate, return_tensors="pt")
    return inputs

def predict_emotion(audio_path):
    """ Predice l'emozione dal file audio """
    if audio_path.endswith(".mp3"):
        print("⚠️ Convertendo MP3 in WAV per evitare problemi di lettura...")
        audio_path = convert_mp3_to_wav(audio_path)
        if not audio_path:
            return None

    inputs = preprocess_audio(audio_path, feature_extractor)
    if inputs is None:
        return None

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    inputs = {key: value.to(device) for key, value in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    probabilities = torch.nn.functional.softmax(logits, dim=-1).squeeze().tolist()

    sorted_emotions = sorted(
        [(id2label[i], prob) for i, prob in enumerate(probabilities)],
        key=lambda x: x[1],
        reverse=True
    )

    return sorted_emotions