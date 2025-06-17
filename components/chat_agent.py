# components/chat_agent.py
import openai
import time
from components.chat_model_interface import ChatModelInterface

class ChatAgent(ChatModelInterface):
    """Wrapper per OpenAI GPT-4o-mini (o altro modello compatibile)."""
    def __init__(self, api_key, temperature: float = 0.7, top_p: float = 0.9):
        openai.api_key = api_key
        self.temperature = temperature
        self.top_p = top_p
        self._last_metadata = {}

    def get_response(self, messages):
        """
        Ritorna la risposta del modello **e** salva le metriche di utilizzo
        accessibili tramite ``get_last_metadata()``.
        """
        try:
            client = openai.OpenAI()
            start  = time.time()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=self.temperature,
                top_p=self.top_p,
                messages=messages
            )
            latency_ms = (time.time() - start) * 1000
            usage      = getattr(response, "usage", None)
            self._last_metadata = {
                "model_name": "gpt-4o-mini",
                "temperature": self.temperature,
                "top_p": self.top_p,
                "prompt_tokens": getattr(usage, "prompt_tokens", None),
                "completion_tokens": getattr(usage, "completion_tokens", None),
                "llm_latency_ms": latency_ms
            }
            return response.choices[0].message.content
        except Exception as e:
            print(f"[ChatAgent] Errore OpenAI: {e}")
            self._last_metadata = {}
            return f"Errore: {e}"

    def get_last_metadata(self):
        """Restituisce le metriche dell'ultima chiamata LLM."""
        return getattr(self, "_last_metadata", {})