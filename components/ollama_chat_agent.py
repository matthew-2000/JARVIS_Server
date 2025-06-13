# components/ollama_chat_agent.py
import requests
from components.chat_model_interface import ChatModelInterface

class OllamaChatAgent(ChatModelInterface):
    """Wrapper per modello locale servito da Ollama (`/api/generate`)."""
    def __init__(self, model_name="llama3.2", host="http://localhost:11434"):
        self.model   = model_name
        self.api_url = f"{host}/api/generate"

    def get_response(self, messages):
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        try:
            r = requests.post(self.api_url, json={"model": self.model, "prompt": prompt, "stream": False})
            return r.json().get("response", "").strip() if r.ok else f"[Ollama] {r.status_code}: {r.text}"
        except Exception as e:
            print(f"[OllamaChatAgent] Errore: {e}")
            return f"Errore: {e}"