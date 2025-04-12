import openai
from components.chat_model_interface import ChatModelInterface


class ChatAgent(ChatModelInterface):
    def __init__(self, api_key):
        openai.api_key = api_key

    def get_response(self, messages):
        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[ChatAgent] Errore nella chiamata: {e}")
            return f"Errore: {e}"
