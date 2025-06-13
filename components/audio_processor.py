# components/audio_processor.py
import os
import subprocess
import soundfile as sf
import numpy as np

class AudioProcessor:
    """Utility per normalizzare e caricare audio mono 16 kHz."""
    def __init__(self, target_sr=16000):
        self.target_sr = target_sr

    def convert_to_wav(self, audio_path):
        """Converte mp3/ogg ecc. in wav mono 16 kHz (ritorna path wav)."""
        if audio_path.lower().endswith(".wav"):
            return audio_path
        wav_path = os.path.splitext(audio_path)[0] + ".wav"
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", audio_path, "-ac", "1", "-ar", str(self.target_sr), wav_path],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return wav_path
        except Exception as e:
            print(f"[AudioProcessor] Errore conversione: {e}")
            return None

    def load_audio(self, path, max_duration_sec):
        """Carica e normalizza SENZA padding."""
        try:
            audio_array, sr = sf.read(path)
        except Exception as e:
            print(f"[AudioProcessor] Errore lettura: {e}")
            return None

        max_len = int(self.target_sr * max_duration_sec)
        if len(audio_array) > max_len:
            audio_array = audio_array[:max_len]

        # normalizza picco
        max_val = np.max(np.abs(audio_array))
        if max_val > 0:
            audio_array = audio_array / max_val
        return audio_array
