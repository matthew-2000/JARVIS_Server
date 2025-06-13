# components/audio_accumulator.py
import numpy as np

class AudioAccumulator:
    """
    Raggruppa spezzoni audio per utente finché la durata totale supera N secondi.
    Dopo l'inferenza il buffer viene azzerato.
    """
    def __init__(self, target_sr=16_000, threshold_sec=30):
        self.target_sr  = target_sr
        self.threshold  = threshold_sec
        self._buffers   = {}       # { user_id: list[np.ndarray] }

    # --- API ---
    def add_chunk(self, user_id, audio_array):
        self._buffers.setdefault(user_id, []).append(audio_array)

    def should_infer(self, user_id):
        total_len = sum(len(b) for b in self._buffers.get(user_id, []))
        return total_len >= self.threshold * self.target_sr

    def pop_concat(self, user_id):
        """Concatena e rimuove il buffer utente se presente, altrimenti None."""
        chunks = self._buffers.pop(user_id, None)
        if not chunks:
            return None
        return np.concatenate(chunks)
