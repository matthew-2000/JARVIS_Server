import time

class EmotionMemory:
    """
    Tiene l'ultimo vettore emozioni per ogni utente, con un TTL.
    Se le emozioni sono più vecchie del TTL, non vengono restituite.
    """
    def __init__(self, ttl_sec=30):
        self.ttl  = ttl_sec
        self._map = {}          # {user_id: {"emotions": {...}, "ts": epoch}}

    def update(self, user_id, emotions: dict):
        self._map[user_id] = {"emotions": emotions, "ts": time.time()}

    def get_recent(self, user_id):
        data = self._map.get(user_id)
        if not data:
            return None
        if time.time() - data["ts"] <= self.ttl:
            return data["emotions"]
        return None           # scadute

    def reset(self, user_id):
        self._map.pop(user_id, None)
