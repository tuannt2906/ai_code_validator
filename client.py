import requests
import json
from config import OLLAMA_API_URL

class OllamaClient:
    def __init__(self):
        self.session = requests.Session()

    def generate(self, model: str, prompt: str, timeout: int = 60, keep_alive: bool = False) -> str:
        """
        Gọi API Ollama. 
        keep_alive=False cực quan trọng cho card 6GB VRAM để giải phóng bộ nhớ ngay.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_ctx": 4096
            },
            "keep_alive": "5m" if keep_alive else 0
        }

        try:
            response = self.session.post(
                OLLAMA_API_URL, 
                json=payload, 
                timeout=timeout
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama Connection Error: {str(e)}")