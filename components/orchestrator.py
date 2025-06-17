class Orchestrator:
    """
    Compone il prompt arricchendolo con le emozioni *recenti*
    prese dalla EmotionMemory.
    """
    def __init__(self, chat_agent, conv_manager, emo_memory):
        self.chat_agent   = chat_agent
        self.conv_manager = conv_manager
        self.emo_memory   = emo_memory

    def _build_prompt(self, text, emotions):
        if emotions:
            emo_str = ", ".join([f"{e}: {p}" for e, p in emotions.items()])
            return f"L'utente ha detto: «{text}». Le emozioni rilevate sono {emo_str}. Rispondi in modo appropriato."
        return text

    def generate_response(self, user_id, text):
        emotions = self.emo_memory.get_recent(user_id)
        prompt   = self._build_prompt(text, emotions)

        messages = self.conv_manager.get_history(user_id) + [{"role": "user", "content": prompt}]
        response_text = self.chat_agent.get_response(messages)
        metadata      = getattr(self.chat_agent, "get_last_metadata", lambda: {})()

        self.conv_manager.add_exchange(user_id, prompt, response_text)
        return response_text, metadata