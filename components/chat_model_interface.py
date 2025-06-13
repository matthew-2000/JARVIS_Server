# components/chat_model_interface.py
from abc import ABC, abstractmethod

class ChatModelInterface(ABC):
    @abstractmethod
    def get_response(self, messages):
        """Genera una risposta stile ChatGPT dato un array di dict {role, content}."""
        pass
