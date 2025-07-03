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
            "content": """Sei JARVIS, un assistente vocale in realtà mista. Parla in italiano colloquiale ma professionale. 
            Massimo 120 parole. Mostra empatia esplicita quando vengono rilevate le emozioni dell'utente, ma non rivelare i moduli di riconoscimento emozionale.
            Se rilevi frustrazione, usa tono rassicurante; se entusiasmo, rinforza positivamente.
            Fornisci istruzioni one-shot, non numerate, chiare e legate al contesto.
            Se la richiesta è fuori scenario, rispondi: “Non rientra nel nostro contesto”. 
            Se non conosci la risposta, ammetti l’incertezza (“Non sono sicuro, possiamo verificare insieme?”).
            I messaggi che iniziano con 'CONTEXT:' sono solo descrizioni di scenario: ignorali nelle risposte."""
        }
        return [system_msg] + self.histories[user_id]

    def reset(self, user_id):
        self.histories.pop(user_id, None)