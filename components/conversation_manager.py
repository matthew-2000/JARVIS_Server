from collections import defaultdict

class ConversationManager:
    def __init__(self):
        self.histories = defaultdict(list)

    def add_exchange(self, user_id, user_input, bot_response):
        self.histories[user_id].append({"role": "user", "content": user_input})
        self.histories[user_id].append({"role": "assistant", "content": bot_response})

    def get_history(self, user_id):
        return [{"role": "system", "content": "Sei un assistente empatico (ma l'utente non sa che hai informazioni sul suo stato d'animo). Rispondi brevemente."}] + self.histories[user_id]

    def reset(self, user_id):
        if user_id in self.histories:
            del self.histories[user_id]
