
from .chat import Chat

class Groq:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.chat = Chat(api_key)
