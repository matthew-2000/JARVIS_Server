# components/orchestrator.py
class Orchestrator:
    """
    Compone il prompt (testo + emozioni se presenti),
    interroga l'LLM e aggiorna la conversazione.
    """
    def __init__(self, chat_agent, conv_manager):
        self.chat_agent   = chat_agent
        self.conv_manager = conv_manager

    def _build_prompt(self, text, emotions):
        if emotions:
            emo_str = ", ".join([f"{e}: {p}" for e, p in emotions.items()])
            return f"L'utente ha detto: «{text}». Le emozioni rilevate sono {emo_str}. Rispondi in modo appropriato."
        return text

    def generate_response(self, user_id, text, emotions=None):
        prompt    = self._build_prompt(text, emotions)
        messages  = self.conv_manager.get_history(user_id) + [{"role": "user", "content": prompt}]
        response  = self.chat_agent.get_response(messages)
        self.conv_manager.add_exchange(user_id, prompt, response)
        return response
