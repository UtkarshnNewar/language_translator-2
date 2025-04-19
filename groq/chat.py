
import requests

class ChatCompletionResponse:
    def __init__(self, content: str):
        self.choices = [type("Message", (), {"message": type("Content", (), {"content": content})()})]

class Chat:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"

    def completions(self):
        return self

    def create(self, model, messages, temperature=0.7, max_tokens=1000, top_p=1, stream=False, stop=None):
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": stream,
            "stop": stop
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]
        return ChatCompletionResponse(content)
