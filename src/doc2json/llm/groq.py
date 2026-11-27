import os

import requests


class GroqLLM:
    def __init__(self, model_id: str | None = None, api_key: str | None = None):
        self.api_key = api_key or os.environ.get('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError('Defina a variável de ambiente GROQ_API_KEY.')

        self.model_id = model_id or os.environ.get('GROQ_MODEL_ID', 'qwen/qwen3.8-27b')
        self.base_url = 'https://api.groq.com/openai/v1/chat/completions'

    def complete(self, prompt: str) -> str:
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'model': self.model_id,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0,
            'max_tokens': 2000,
        }

        response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        return data['choices'][0]['message']['content']
