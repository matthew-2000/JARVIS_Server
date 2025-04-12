import requests
from components.chat_model_interface import ChatModelInterface


class OllamaChatAgent(ChatModelInterface):
    def __init__(self, model_name="llama3.2", host="http://localhost:11434"):
        self.model = model_name
        self.api_url = f"{host}/api/generate"

    def get_response(self, messages):
        # Concatena i messaggi in uno stile semplice
        full_prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

        try:
            response = requests.post(self.api_url, json={
                "model": self.model,
                "prompt": full_prompt,
                "stream": False
            })

            if response.ok:
                return response.json().get("response", "").strip()
            else:
                return f"[Ollama] Errore HTTP: {response.status_code} - {response.text}"

        except Exception as e:
            print(f"[OllamaChatAgent] Errore nella chiamata a Ollama: {e}")
            return f"Errore: {e}"