# client.py
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import OLLAMA_API_URL

class OllamaClient:
    def __init__(self):
        self.session = requests.Session()

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError))
    )
    def generate(self, model: str, prompt: str, timeout: int = 60, keep_alive: bool = False) -> str:
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
            data = response.json()
            return data.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            # Log lỗi ra file nếu cần thiết
            raise e