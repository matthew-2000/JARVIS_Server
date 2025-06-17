# components/ollama_chat_agent.py
import requests
import time
from components.chat_model_interface import ChatModelInterface

class OllamaChatAgent(ChatModelInterface):
    """Wrapper per modello locale servito da Ollama (`/api/generate`)."""
    def __init__(self, model_name="llama3.2", host="http://localhost:11434", temperature: float = 0.7, top_p: float = 0.9):
        self.model   = model_name
        self.api_url = f"{host}/api/generate"
        self.temperature = temperature
        self.top_p = top_p
        self._last_metadata = {}

    def get_response(self, messages):
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        start  = time.time()
        try:
            r = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": self.temperature,
                    "top_p": self.top_p
                }
            )
            latency_ms = (time.time() - start) * 1000
            text = r.json().get("response", "").strip() if r.ok else f"[Ollama] {r.status_code}: {r.text}"
        except Exception as e:
            print(f"[OllamaChatAgent] Errore: {e}")
            text = f"Errore: {e}"
            latency_ms = None
        # token usage non disponibile con Ollama → None
        self._last_metadata = {
            "model_name": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "prompt_tokens": None,
            "completion_tokens": None,
            "llm_latency_ms": latency_ms
        }
        return text

    def get_last_metadata(self):
        """Restituisce le metriche dell'ultima chiamata LLM."""
        return getattr(self, "_last_metadata", {})