from llm.ollama_client import call_ollama
from pathlib import Path


class PerformanceValidator:
    def __init__(self):
        self.prompt_template = Path("prompts/performance.txt").read_text()

    def run(self, hotspots: list[str]) -> str:
        joined = "\n\n".join(hotspots)
        prompt = self.prompt_template.replace("{{code}}", joined)
        return call_ollama("qwen2.5-coder:7b", prompt)
