from abc import ABC, abstractmethod


class ChatModelInterface(ABC):
    @abstractmethod
    def get_response(self, messages):
        """
        Genera una risposta da una lista di messaggi in stile ChatGPT.

        :param messages: Lista di dizionari con 'role' (es. 'user', 'assistant') e 'content'.

        Esempio:
        [
            {"role": "user", "content": "Ciao, come stai?"},
            {"role": "assistant", "content": "Sto bene, grazie!"}
        ]
        """
        pass
