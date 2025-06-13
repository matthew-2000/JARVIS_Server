# components/conversation_manager.py
from collections import defaultdict

class ConversationManager:
    """Mantiene lo storico dei messaggi per ogni utente (in-memory)."""
    def __init__(self):
        self.histories = defaultdict(list)

    def add_exchange(self, user_id, user_input, bot_response):
        self.histories[user_id].extend([
            {"role": "user",      "content": user_input},
            {"role": "assistant", "content": bot_response},
        ])

    def get_history(self, user_id):
        system_msg = {
            "role": "system",
            "content": "Sei un assistente empatico (ma l'utente non sa che rilevi le sue emozioni). Rispondi brevemente."
        }
        return [system_msg] + self.histories[user_id]

    def reset(self, user_id):
        self.histories.pop(user_id, None)